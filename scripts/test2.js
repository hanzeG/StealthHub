'use strict';
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

// ---------------------------
// Configuration
// ---------------------------
const INITIAL_ROOT = "0xf46a7a418a6466497be26636a906ad8efd56f663199b679e63e70bc8666566cf";
const TREE_DEPTH = 16; // Depth of the Incremental Merkle Tree
const MMR_INSERTION_COUNT = 65536; // 2^16
const IMT_INSERTION_COUNT = 65536; // 2^16

const SAMPLE_COMMITMENT = "0xf46a7a418a6466497be26636a906ad8efd56f663199b679e63e70bc8666566cf";

/**
 * Prints a single‑line progress indicator to the console.
 * @param {number} current - Current completed iterations (1‑based).
 * @param {number} total   - Total iterations.
 * @param {string} label   - Descriptive label (e.g., "MMR", "IMT").
 */
function printProgress(current, total, label) {
    const percent = ((current / total) * 100).toFixed(2);
    process.stdout.write(`\r${label} progress: ${current}/${total} (${percent}%)`);
    if (current === total) process.stdout.write('\n');
}

async function main() {
    // Deploy Poseidon2 hash function
    const poseidon2Factory = await ethers.getContractFactory("Poseidon2Yul");
    const poseidon2 = await poseidon2Factory.deploy();
    await poseidon2.waitForDeployment();
    const poseidon2Address = await poseidon2.getAddress();
    console.log("Poseidon2 deployed at:", poseidon2Address);

    // Deploy Merkle Mountain Range (MMR) contract
    const mmrFactory = await ethers.getContractFactory("Mmr");
    const mmr = await mmrFactory.deploy(INITIAL_ROOT, poseidon2Address);
    await mmr.waitForDeployment();
    const mmrAddress = await mmr.getAddress();
    console.log("MMR deployed at:", mmrAddress);

    const mmrInsertionCount = MMR_INSERTION_COUNT;
    const mmrGasUsed = [];

    for (let i = 0; i < mmrInsertionCount; i++) {
        const txResponse = await mmr.insert(SAMPLE_COMMITMENT);
        const receipt = await txResponse.wait();
        mmrGasUsed.push(receipt.gasUsed.toString());
        printProgress(i + 1, mmrInsertionCount, "MMR");
    }

    console.log("MMR - Gas used per insert:", mmrGasUsed);

    // Deploy Incremental Merkle Tree (IMT) contract
    const imtFactory = await ethers.getContractFactory("Imt");
    const imt = await imtFactory.deploy(TREE_DEPTH, poseidon2Address);
    await imt.waitForDeployment();
    const imtAddress = await imt.getAddress();
    console.log("IMT deployed at:", imtAddress);

    const imtInsertionCount = IMT_INSERTION_COUNT;
    const imtGasUsed = [];

    for (let i = 0; i < imtInsertionCount; i++) {
        const txResponse = await imt.insertLeaf(SAMPLE_COMMITMENT);
        const receipt = await txResponse.wait();
        imtGasUsed.push(receipt.gasUsed.toString());
        printProgress(i + 1, imtInsertionCount, "IMT");
    }

    console.log("Incremental Merkle Tree - Gas used per insert:", imtGasUsed);

    // Persist gas usage metrics to JSON
    const gasData = {
        mmrGas: mmrGasUsed,
        imtGas: imtGasUsed,
    };

    const outputFilePath = path.join(__dirname, "../data/16_gas_used.json");
    fs.writeFileSync(outputFilePath, JSON.stringify(gasData, null, 2));

    console.log(`Gas usage data saved to ${outputFilePath}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error:", error);
        process.exit(1);
    });