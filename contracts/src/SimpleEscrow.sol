// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title SimpleEscrow
 * @author Agentic Commerce Team
 * @notice A simple escrow contract for agentic commerce transactions on Arc Network
 * @dev Supports ETH escrow between buyer and seller with 24-hour timeout for refunds
 */
contract SimpleEscrow is ReentrancyGuard {
    // ============ Constants ============

    /// @notice Duration after which buyer can claim refund if seller doesn't deliver
    uint256 public constant ESCROW_TIMEOUT = 24 hours;

    // ============ Enums ============

    /// @notice Possible states of an escrow
    enum EscrowState {
        Active,     // Escrow created, awaiting release or refund
        Released,   // Funds released to seller
        Refunded    // Funds refunded to buyer
    }

    // ============ Structs ============

    /// @notice Escrow data structure
    struct Escrow {
        address buyer;
        address seller;
        uint256 amount;
        uint256 createdAt;
        EscrowState state;
    }

    // ============ State Variables ============

    /// @notice Counter for generating unique escrow IDs
    uint256 private _escrowIdCounter;

    /// @notice Mapping from escrow ID to escrow data
    mapping(uint256 => Escrow) private _escrows;

    // ============ Events ============

    /// @notice Emitted when a new escrow is created
    /// @param escrowId The unique identifier of the escrow
    /// @param buyer The address of the buyer
    /// @param seller The address of the seller
    /// @param amount The amount of ETH escrowed
    event EscrowCreated(
        uint256 indexed escrowId,
        address indexed buyer,
        address indexed seller,
        uint256 amount
    );

    /// @notice Emitted when funds are released to the seller
    /// @param escrowId The unique identifier of the escrow
    /// @param seller The address of the seller
    /// @param amount The amount of ETH released
    event FundsReleased(
        uint256 indexed escrowId,
        address indexed seller,
        uint256 amount
    );

    /// @notice Emitted when funds are refunded to the buyer
    /// @param escrowId The unique identifier of the escrow
    /// @param buyer The address of the buyer
    /// @param amount The amount of ETH refunded
    event FundsRefunded(
        uint256 indexed escrowId,
        address indexed buyer,
        uint256 amount
    );

    // ============ Errors ============

    /// @notice Thrown when seller address is zero
    error InvalidSeller();

    /// @notice Thrown when escrow amount is zero
    error InvalidAmount();

    /// @notice Thrown when msg.value doesn't match amount
    error AmountMismatch();

    /// @notice Thrown when escrow doesn't exist
    error EscrowNotFound();

    /// @notice Thrown when escrow is not in Active state
    error EscrowNotActive();

    /// @notice Thrown when caller is not the buyer
    error OnlyBuyer();

    /// @notice Thrown when caller is not seller and timeout hasn't passed
    error RefundNotAllowed();

    /// @notice Thrown when ETH transfer fails
    error TransferFailed();

    // ============ External Functions ============

    /**
     * @notice Creates a new escrow between buyer (msg.sender) and seller
     * @param seller The address of the seller who will receive funds upon release
     * @param amount The amount of ETH to escrow (must match msg.value)
     * @return escrowId The unique identifier of the created escrow
     */
    function createEscrow(
        address seller,
        uint256 amount
    ) external payable nonReentrant returns (uint256 escrowId) {
        // Validate inputs
        if (seller == address(0)) revert InvalidSeller();
        if (amount == 0) revert InvalidAmount();
        if (msg.value != amount) revert AmountMismatch();

        // Generate escrow ID and increment counter
        escrowId = _escrowIdCounter++;

        // Create escrow
        _escrows[escrowId] = Escrow({
            buyer: msg.sender,
            seller: seller,
            amount: amount,
            createdAt: block.timestamp,
            state: EscrowState.Active
        });

        emit EscrowCreated(escrowId, msg.sender, seller, amount);
    }

    /**
     * @notice Releases escrowed funds to the seller
     * @dev Only the buyer can release funds. This confirms successful delivery.
     * @param escrowId The unique identifier of the escrow
     */
    function releaseToSeller(uint256 escrowId) external nonReentrant {
        Escrow storage escrow = _escrows[escrowId];

        // Validate escrow exists and is active
        if (escrow.buyer == address(0)) revert EscrowNotFound();
        if (escrow.state != EscrowState.Active) revert EscrowNotActive();

        // Only buyer can release funds
        if (msg.sender != escrow.buyer) revert OnlyBuyer();

        // Update state before transfer (CEI pattern)
        escrow.state = EscrowState.Released;
        uint256 amount = escrow.amount;
        address seller = escrow.seller;

        // Transfer funds to seller
        (bool success, ) = seller.call{value: amount}("");
        if (!success) revert TransferFailed();

        emit FundsReleased(escrowId, seller, amount);
    }

    /**
     * @notice Refunds escrowed funds to the buyer
     * @dev Can be called by:
     *      - Seller at any time (voluntary refund)
     *      - Anyone after 24-hour timeout (automatic refund eligibility)
     * @param escrowId The unique identifier of the escrow
     */
    function refundBuyer(uint256 escrowId) external nonReentrant {
        Escrow storage escrow = _escrows[escrowId];

        // Validate escrow exists and is active
        if (escrow.buyer == address(0)) revert EscrowNotFound();
        if (escrow.state != EscrowState.Active) revert EscrowNotActive();

        // Check refund authorization
        bool isSeller = msg.sender == escrow.seller;
        bool isTimedOut = block.timestamp >= escrow.createdAt + ESCROW_TIMEOUT;

        if (!isSeller && !isTimedOut) revert RefundNotAllowed();

        // Update state before transfer (CEI pattern)
        escrow.state = EscrowState.Refunded;
        uint256 amount = escrow.amount;
        address buyer = escrow.buyer;

        // Transfer funds to buyer
        (bool success, ) = buyer.call{value: amount}("");
        if (!success) revert TransferFailed();

        emit FundsRefunded(escrowId, buyer, amount);
    }

    // ============ View Functions ============

    /**
     * @notice Returns the details of an escrow
     * @param escrowId The unique identifier of the escrow
     * @return buyer The address of the buyer
     * @return seller The address of the seller
     * @return amount The escrowed amount in wei
     * @return createdAt The timestamp when the escrow was created
     * @return state The current state of the escrow
     */
    function getEscrow(uint256 escrowId) external view returns (
        address buyer,
        address seller,
        uint256 amount,
        uint256 createdAt,
        EscrowState state
    ) {
        Escrow storage escrow = _escrows[escrowId];
        if (escrow.buyer == address(0)) revert EscrowNotFound();

        return (
            escrow.buyer,
            escrow.seller,
            escrow.amount,
            escrow.createdAt,
            escrow.state
        );
    }

    /**
     * @notice Returns the current escrow counter (total escrows created)
     * @return The number of escrows created
     */
    function getEscrowCount() external view returns (uint256) {
        return _escrowIdCounter;
    }

    /**
     * @notice Checks if an escrow is eligible for timeout refund
     * @param escrowId The unique identifier of the escrow
     * @return True if 24 hours have passed since creation
     */
    function isTimedOut(uint256 escrowId) external view returns (bool) {
        Escrow storage escrow = _escrows[escrowId];
        if (escrow.buyer == address(0)) revert EscrowNotFound();

        return block.timestamp >= escrow.createdAt + ESCROW_TIMEOUT;
    }

    /**
     * @notice Returns time remaining until timeout refund is available
     * @param escrowId The unique identifier of the escrow
     * @return Seconds until timeout, or 0 if already timed out
     */
    function timeUntilTimeout(uint256 escrowId) external view returns (uint256) {
        Escrow storage escrow = _escrows[escrowId];
        if (escrow.buyer == address(0)) revert EscrowNotFound();

        uint256 timeoutAt = escrow.createdAt + ESCROW_TIMEOUT;
        if (block.timestamp >= timeoutAt) return 0;
        return timeoutAt - block.timestamp;
    }
}
