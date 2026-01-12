// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Script} from "forge-std/Script.sol";
import {SimpleEscrow} from "../src/SimpleEscrow.sol";

contract DeployScript is Script {
    function run() external returns (SimpleEscrow) {
        uint256 deployerPrivateKey = vm.envUint("AGENT_PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);
        SimpleEscrow escrow = new SimpleEscrow();
        vm.stopBroadcast();
        return escrow;
    }
}
