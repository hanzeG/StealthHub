'use strict';
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");
// ---------------------------
// Configuration
// ---------------------------
const INITIAL_ROOT = "0xf46a7a418a6466497be26636a906ad8efd56f663199b679e63e70bc8666566cf";
const INSERTION_COUNT = 65536;            // 2^16
const SAMPLE_COMMITMENT = "0x006a7a418a6466497be26636a906ad8efd56f663199b679e63e70bc8666566cf";
const SAMPLE_DEPOSIT_VALUE = 100000000000n;

/**
 * Prints a single‑line progress indicator.
 * @param {number} current Completed iterations (1‑based).
 * @param {number} total   Total iterations.
 * @param {string} label   Descriptive label.
 */
function printProgress(current, total, label) {
    const percent = ((current / total) * 100).toFixed(2);
    process.stdout.write(`\r${label} progress: ${current}/${total} (${percent}%)`);
    if (current === total) process.stdout.write("\n");
}

const zkProof = [["0x26472964da7eafd6bfddbcc5556b87e069b98649afb918d5ffb99f2eb18a2536", "0x077db48ba7bc9ab0e1305276d3d6d2f0f6ea994c91ae3f2b70bcd34d8acfab04"], [["0x1dd86a393222110fb157ad41470271e68f6268b4029f9c70f392099e4bb22c9b", "0x09a387779963a97c5d126f46dfc85a0f4f5be60fccc820feed335f2e410ccf42"], ["0x0d60f88d1861131fd4555d124b01f1b44d4aa2f45130bcbbec496257ef9261e0", "0x2c9f7aa08444e6057cc390fd876c8a29013da8ef2925074143c80b57763b41b1"]], ["0x0c2def9770b76eab8c29ab82c98c50c729d1f8994695e06f5f2cae9605d510ed", "0x1be4185e550200f86bdc749aac64fd3dd7986a69dc7f0516bf414949a990ec05"], ["0x0000000000000000000000000000000000000000000000000000000000000001"]]

async function main() {
    // Deploy Poseidon2 hash function contract
    const poseidon2Factory = await ethers.getContractFactory("Poseidon2Yul");
    const poseidon2 = await poseidon2Factory.deploy();
    await poseidon2.waitForDeployment();
    const poseidon2Address = await poseidon2.getAddress();
    console.log("Poseidon2 deployed at:", poseidon2Address);

    // Deploy Verifier1 contract
    const verifierFactory1 = await ethers.getContractFactory("Groth16Verifier");
    const verifier1 = await verifierFactory1.deploy();
    await verifier1.waitForDeployment();
    const verifier1Address = await verifier1.getAddress();
    console.log("Verifier1 deployed at:", verifier1Address);

    // Deploy Verifier2 contract
    const verifierFactory2 = await ethers.getContractFactory("Groth16Verifier");
    const verifier2 = await verifierFactory2.deploy();
    await verifier2.waitForDeployment();
    const verifier2Address = await verifier2.getAddress();
    console.log("Verifier2 deployed at:", verifier2Address);

    // Deploy EthShm contract
    const EthShmFactory = await ethers.getContractFactory("EthShm");
    const EthShm = await EthShmFactory.deploy(verifier1Address, verifier2Address, poseidon2Address, INITIAL_ROOT);
    await EthShm.waitForDeployment();
    const EthShmAddress = await EthShm.getAddress();
    console.log("EthShm deployed at:", EthShmAddress);

    const insertionCount = INSERTION_COUNT;
    const mmrGasUsed = [];

    for (let i = 0; i < insertionCount; i++) {
        const txResponse = await EthShm.shieldedTransfer(SAMPLE_COMMITMENT, SAMPLE_COMMITMENT, zkProof, SAMPLE_DEPOSIT_VALUE);
        const receipt = await txResponse.wait();
        mmrGasUsed.push(receipt.gasUsed.toString());
        printProgress(i + 1, insertionCount, "EthShm");
    }

    console.log("EthShm - Gas used per insert:", mmrGasUsed);

    // Store gas usage data in a JSON file
    const gasData = {
        mmrGas: mmrGasUsed,
    };

    const outputFilePath = path.join(__dirname, "../data/shm_st_16_31_gas_used.json");
    fs.writeFileSync(outputFilePath, JSON.stringify(gasData, null, 2));

    console.log(`Gas usage data saved to ${outputFilePath}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error("Error:", error);
        process.exit(1);
    });