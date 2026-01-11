// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console} from "forge-std/Test.sol";
import {SimpleEscrow} from "../src/SimpleEscrow.sol";

/**
 * @title SimpleEscrowTest
 * @notice Comprehensive test suite for SimpleEscrow contract
 */
contract SimpleEscrowTest is Test {
    SimpleEscrow public escrow;

    address public buyer;
    address public seller;
    address public attacker;

    uint256 public constant ESCROW_AMOUNT = 1 ether;
    uint256 public constant TIMEOUT = 24 hours;

    // Events for testing
    event EscrowCreated(uint256 indexed escrowId, address indexed buyer, address indexed seller, uint256 amount);
    event FundsReleased(uint256 indexed escrowId, address indexed seller, uint256 amount);
    event FundsRefunded(uint256 indexed escrowId, address indexed buyer, uint256 amount);

    function setUp() public {
        escrow = new SimpleEscrow();

        buyer = makeAddr("buyer");
        seller = makeAddr("seller");
        attacker = makeAddr("attacker");

        // Fund accounts
        vm.deal(buyer, 10 ether);
        vm.deal(seller, 1 ether);
        vm.deal(attacker, 1 ether);
    }

    // ============ createEscrow Tests ============

    function test_CreateEscrow_Success() public {
        vm.prank(buyer);

        vm.expectEmit(true, true, true, true);
        emit EscrowCreated(0, buyer, seller, ESCROW_AMOUNT);

        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        assertEq(escrowId, 0);
        assertEq(address(escrow).balance, ESCROW_AMOUNT);

        (address _buyer, address _seller, uint256 _amount, uint256 _createdAt, SimpleEscrow.EscrowState _state) = escrow.getEscrow(escrowId);

        assertEq(_buyer, buyer);
        assertEq(_seller, seller);
        assertEq(_amount, ESCROW_AMOUNT);
        assertEq(_createdAt, block.timestamp);
        assertEq(uint256(_state), uint256(SimpleEscrow.EscrowState.Active));
    }

    function test_CreateEscrow_MultipleEscrows() public {
        vm.startPrank(buyer);

        uint256 id1 = escrow.createEscrow{value: 1 ether}(seller, 1 ether);
        uint256 id2 = escrow.createEscrow{value: 2 ether}(seller, 2 ether);
        uint256 id3 = escrow.createEscrow{value: 0.5 ether}(seller, 0.5 ether);

        vm.stopPrank();

        assertEq(id1, 0);
        assertEq(id2, 1);
        assertEq(id3, 2);
        assertEq(escrow.getEscrowCount(), 3);
        assertEq(address(escrow).balance, 3.5 ether);
    }

    function test_CreateEscrow_RevertInvalidSeller() public {
        vm.prank(buyer);
        vm.expectRevert(SimpleEscrow.InvalidSeller.selector);
        escrow.createEscrow{value: ESCROW_AMOUNT}(address(0), ESCROW_AMOUNT);
    }

    function test_CreateEscrow_RevertInvalidAmount() public {
        vm.prank(buyer);
        vm.expectRevert(SimpleEscrow.InvalidAmount.selector);
        escrow.createEscrow{value: 0}(seller, 0);
    }

    function test_CreateEscrow_RevertAmountMismatch() public {
        vm.prank(buyer);
        vm.expectRevert(SimpleEscrow.AmountMismatch.selector);
        escrow.createEscrow{value: 0.5 ether}(seller, ESCROW_AMOUNT);
    }

    function testFuzz_CreateEscrow(address _seller, uint256 _amount) public {
        vm.assume(_seller != address(0));
        vm.assume(_amount > 0 && _amount <= 10 ether);

        vm.deal(buyer, _amount);
        vm.prank(buyer);

        uint256 escrowId = escrow.createEscrow{value: _amount}(_seller, _amount);

        (address b, address s, uint256 a, , ) = escrow.getEscrow(escrowId);
        assertEq(b, buyer);
        assertEq(s, _seller);
        assertEq(a, _amount);
    }

    // ============ releaseToSeller Tests ============

    function test_ReleaseToSeller_Success() public {
        // Create escrow
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        uint256 sellerBalanceBefore = seller.balance;

        // Release funds
        vm.prank(buyer);
        vm.expectEmit(true, true, false, true);
        emit FundsReleased(escrowId, seller, ESCROW_AMOUNT);
        escrow.releaseToSeller(escrowId);

        // Verify
        assertEq(seller.balance, sellerBalanceBefore + ESCROW_AMOUNT);
        assertEq(address(escrow).balance, 0);

        (, , , , SimpleEscrow.EscrowState state) = escrow.getEscrow(escrowId);
        assertEq(uint256(state), uint256(SimpleEscrow.EscrowState.Released));
    }

    function test_ReleaseToSeller_RevertNotBuyer() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        // Seller tries to release
        vm.prank(seller);
        vm.expectRevert(SimpleEscrow.OnlyBuyer.selector);
        escrow.releaseToSeller(escrowId);

        // Attacker tries to release
        vm.prank(attacker);
        vm.expectRevert(SimpleEscrow.OnlyBuyer.selector);
        escrow.releaseToSeller(escrowId);
    }

    function test_ReleaseToSeller_RevertEscrowNotFound() public {
        vm.prank(buyer);
        vm.expectRevert(SimpleEscrow.EscrowNotFound.selector);
        escrow.releaseToSeller(999);
    }

    function test_ReleaseToSeller_RevertAlreadyReleased() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        vm.prank(buyer);
        escrow.releaseToSeller(escrowId);

        vm.prank(buyer);
        vm.expectRevert(SimpleEscrow.EscrowNotActive.selector);
        escrow.releaseToSeller(escrowId);
    }

    // ============ refundBuyer Tests ============

    function test_RefundBuyer_BySeller() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        uint256 buyerBalanceBefore = buyer.balance;

        // Seller refunds
        vm.prank(seller);
        vm.expectEmit(true, true, false, true);
        emit FundsRefunded(escrowId, buyer, ESCROW_AMOUNT);
        escrow.refundBuyer(escrowId);

        // Verify
        assertEq(buyer.balance, buyerBalanceBefore + ESCROW_AMOUNT);
        assertEq(address(escrow).balance, 0);

        (, , , , SimpleEscrow.EscrowState state) = escrow.getEscrow(escrowId);
        assertEq(uint256(state), uint256(SimpleEscrow.EscrowState.Refunded));
    }

    function test_RefundBuyer_AfterTimeout() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        // Warp time past timeout
        vm.warp(block.timestamp + TIMEOUT + 1);

        uint256 buyerBalanceBefore = buyer.balance;

        // Anyone can refund after timeout
        vm.prank(attacker);
        escrow.refundBuyer(escrowId);

        assertEq(buyer.balance, buyerBalanceBefore + ESCROW_AMOUNT);
    }

    function test_RefundBuyer_RevertBeforeTimeout() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        // Warp time but not enough
        vm.warp(block.timestamp + TIMEOUT - 1);

        // Attacker tries to refund
        vm.prank(attacker);
        vm.expectRevert(SimpleEscrow.RefundNotAllowed.selector);
        escrow.refundBuyer(escrowId);
    }

    function test_RefundBuyer_RevertAlreadyRefunded() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        vm.prank(seller);
        escrow.refundBuyer(escrowId);

        vm.prank(seller);
        vm.expectRevert(SimpleEscrow.EscrowNotActive.selector);
        escrow.refundBuyer(escrowId);
    }

    // ============ View Function Tests ============

    function test_GetEscrow_RevertNotFound() public {
        vm.expectRevert(SimpleEscrow.EscrowNotFound.selector);
        escrow.getEscrow(0);
    }

    function test_IsTimedOut() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        assertFalse(escrow.isTimedOut(escrowId));

        vm.warp(block.timestamp + TIMEOUT);
        assertTrue(escrow.isTimedOut(escrowId));
    }

    function test_TimeUntilTimeout() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        assertEq(escrow.timeUntilTimeout(escrowId), TIMEOUT);

        vm.warp(block.timestamp + 1 hours);
        assertEq(escrow.timeUntilTimeout(escrowId), TIMEOUT - 1 hours);

        vm.warp(block.timestamp + TIMEOUT);
        assertEq(escrow.timeUntilTimeout(escrowId), 0);
    }

    function test_GetEscrowCount() public {
        assertEq(escrow.getEscrowCount(), 0);

        vm.prank(buyer);
        escrow.createEscrow{value: 1 ether}(seller, 1 ether);
        assertEq(escrow.getEscrowCount(), 1);

        vm.prank(buyer);
        escrow.createEscrow{value: 1 ether}(seller, 1 ether);
        assertEq(escrow.getEscrowCount(), 2);
    }

    // ============ Security Tests ============

    function test_ReentrancyProtection_Release() public {
        // Deploy malicious seller contract
        MaliciousReceiver malicious = new MaliciousReceiver(address(escrow), MaliciousReceiver.AttackType.Release);

        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(address(malicious), ESCROW_AMOUNT);

        malicious.setEscrowId(escrowId);

        // This should not allow reentrancy
        vm.prank(buyer);
        escrow.releaseToSeller(escrowId);

        // Verify only one transfer occurred
        assertEq(address(malicious).balance, ESCROW_AMOUNT);
        assertEq(address(escrow).balance, 0);
    }

    function test_ReentrancyProtection_Refund() public {
        // Deploy malicious buyer contract
        MaliciousBuyer maliciousBuyer = new MaliciousBuyer(address(escrow));
        vm.deal(address(maliciousBuyer), 2 ether);

        vm.prank(address(maliciousBuyer));
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        maliciousBuyer.setEscrowId(escrowId);

        // Seller refunds - should not allow reentrancy
        vm.prank(seller);
        escrow.refundBuyer(escrowId);

        // Verify only one transfer occurred
        assertEq(address(maliciousBuyer).balance, 2 ether); // 2 - 1 + 1 = 2
        assertEq(address(escrow).balance, 0);
    }

    // ============ Edge Case Tests ============

    function test_ExactTimeoutBoundary() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: ESCROW_AMOUNT}(seller, ESCROW_AMOUNT);

        // At exactly TIMEOUT - 1 second, should fail
        vm.warp(block.timestamp + TIMEOUT - 1);
        vm.prank(attacker);
        vm.expectRevert(SimpleEscrow.RefundNotAllowed.selector);
        escrow.refundBuyer(escrowId);

        // At exactly TIMEOUT, should succeed
        vm.warp(block.timestamp + 1);
        vm.prank(attacker);
        escrow.refundBuyer(escrowId);
    }

    function test_MinimumEscrowAmount() public {
        vm.prank(buyer);
        uint256 escrowId = escrow.createEscrow{value: 1 wei}(seller, 1 wei);

        (, , uint256 amount, , ) = escrow.getEscrow(escrowId);
        assertEq(amount, 1 wei);
    }
}

// ============ Helper Contracts for Testing ============

contract MaliciousReceiver {
    SimpleEscrow public escrow;
    uint256 public escrowId;
    AttackType public attackType;
    bool public attacked;

    enum AttackType { Release, Refund }

    constructor(address _escrow, AttackType _type) {
        escrow = SimpleEscrow(_escrow);
        attackType = _type;
    }

    function setEscrowId(uint256 _id) external {
        escrowId = _id;
    }

    receive() external payable {
        if (!attacked) {
            attacked = true;
            // Attempt reentrancy - this should fail due to ReentrancyGuard
            try escrow.releaseToSeller(escrowId) {} catch {}
        }
    }
}

contract MaliciousBuyer {
    SimpleEscrow public escrow;
    uint256 public escrowId;
    bool public attacked;

    constructor(address _escrow) {
        escrow = SimpleEscrow(_escrow);
    }

    function setEscrowId(uint256 _id) external {
        escrowId = _id;
    }

    receive() external payable {
        if (!attacked) {
            attacked = true;
            // Attempt reentrancy - this should fail due to ReentrancyGuard
            try escrow.refundBuyer(escrowId) {} catch {}
        }
    }
}
