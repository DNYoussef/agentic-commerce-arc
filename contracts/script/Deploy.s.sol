// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {SimpleEscrow} from "../src/SimpleEscrow.sol";

/**
 * @title Deploy
 * @notice Deployment script for SimpleEscrow contract on Arc Network
 * @dev Run with: forge script script/Deploy.s.sol:DeployScript --rpc-url arc --broadcast
 */
contract DeployScript is Script {
    function setUp() public {}

    function run() public {
        // Load private key from environment
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);

        console.log("Deploying SimpleEscrow...");
        console.log("Deployer address:", deployer);
        console.log("Deployer balance:", deployer.balance);

        vm.startBroadcast(deployerPrivateKey);

        // Deploy SimpleEscrow
        SimpleEscrow escrow = new SimpleEscrow();

        vm.stopBroadcast();

        console.log("SimpleEscrow deployed at:", address(escrow));
        console.log("Escrow timeout:", escrow.ESCROW_TIMEOUT(), "seconds (24 hours)");
    }
}

/**
 * @title DeployAndVerify
 * @notice Extended deployment script with verification setup
 * @dev Includes post-deployment verification checks
 */
contract DeployAndVerifyScript is Script {
    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        SimpleEscrow escrow = new SimpleEscrow();

        vm.stopBroadcast();

        // Verify deployment
        require(address(escrow) != address(0), "Deployment failed");
        require(escrow.ESCROW_TIMEOUT() == 24 hours, "Timeout mismatch");
        require(escrow.getEscrowCount() == 0, "Initial count should be 0");

        console.log("=== Deployment Successful ===");
        console.log("Contract:", address(escrow));
        console.log("Network: Arc Testnet");
        console.log("Timeout: 24 hours");
        console.log("");
        console.log("Add to your .env:");
        console.log("ESCROW_CONTRACT=", address(escrow));
    }
}
