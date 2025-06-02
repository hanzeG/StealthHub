'use strict';
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");
// ---------------------------
// Configuration
// ---------------------------
const INITIAL_ROOT = "0xf46a7a418a6466497be26636a906ad8efd56f663199b679e63e70bc8666566cf";
const TREE_HEIGHTS = [4, 8, 16, 31]; // The height of IMT


async function main() {
    // Deploy Poseidon2 hash function contract
    const poseidon2Factory = await ethers.getContractFactory("Poseidon2Yul");
    const poseidon2 = await poseidon2Factory.deploy();
    await poseidon2.waitForDeployment();
    const poseidon2Address = await poseidon2.getAddress();
    console.log("Poseidon2 deployed at:", poseidon2Address);

    // Deploy mmr contract
    const mmrFactory = await ethers.getContractFactory("Mmr");
    const mmr = await mmrFactory.deploy(INITIAL_ROOT, poseidon2Address);
    await mmr.waitForDeployment();
    const mmrAddress = await mmr.getAddress();
    console.log("mmr deployed at:", mmrAddress);

    const gasUsedMMR = [];
    const gasUsedIMT = {};

    const mmrDeployReceipt = await mmr.deploymentTransaction().wait();
    gasUsedMMR.push(mmrDeployReceipt.gasUsed.toString());
    console.log("MMR - Gas used for deployment:", gasUsedMMR[0]);

    for (const height of TREE_HEIGHTS) {
        const imtFactory = await ethers.getContractFactory("Imt");
        const imt = await imtFactory.deploy(height, poseidon2Address);
        await imt.waitForDeployment();
        const imtAddress = await imt.getAddress();
        const receipt = await imt.deploymentTransaction().wait();
        gasUsedIMT[height] = receipt.gasUsed.toString();
        console.log(`IMT (height=${height}) deployed at: ${imtAddress}`);
        console.log(`IMT (height=${height}) - Gas used for deployment: ${gasUsedIMT[height]}`);
    }

    // Store gas usage data in a JSON file
    const gasData = {
        mmrDeployGas: gasUsedMMR,
        imtDeployGas: gasUsedIMT,
    };

    const outputFilePath = path.join(__dirname, "../data/deploy_gas_used.json");
    fs.writeFileSync(outputFilePath, JSON.stringify(gasData, null, 2));

    console.log(`Gas usage data saved to ${outputFilePath}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error:", error);
        process.exit(1);
    });