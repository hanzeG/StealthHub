# StealthHub: A UTXO-based Stealth Address Protocol


# StealthHub README

## 1. Introduction

StealthHub is a protocol that combines a zero‐knowledge proof (ZKP) mixer with a Stealth Address Protocol (SAP). By integrating these two components, StealthHub aims to enhance transaction privacy and unlinkability on blockchain networks. This repository provides:

1. **Circom‐based ZKP implementations**  
   - Circuit definitions for Pedersen and Poseidon hash functions  
   - Mixer circuits utilising the Groth16 proving system (SnarkJS)  
   - Stealth address circuits for RSA‐based and pairing‐based constructions  

2. **JavaScript unit test suite**  
   - Tests for circuit correctness (using Mocha/Chai)  
   - End‐to‐end tests for deposit and withdrawal operations in various implementations

3. **SnarkJS Groth16 performance scripts**  
   - Scripts to measure constraints, proving time and verifier time (memory measurements provided in external benchmarks)

4. **Three on‐chain implementation variants**  
   - **SH‐I**: Incremental Merkle Tree (IMT)-based implementation  
   - **SH‐M**: Merkle Mountain Range (MMR)-based implementation  
   - **SH‐A**: Off-chain aggregation (batching) implementation  

5. **Ethereum smart contracts and test scripts**  
   - Contracts for each variant (SH‐I, SH‐M, SH‐A) written in Solidity  
   - Hardhat scripts for gas benchmarking and automated tests  

6. **Performance visualisation scripts**  
   - Python scripts to generate plots from collected gas and constraint data

7. **Umbra-Protocol comparison submodule**  
   - A direct evaluation of StealthHub versus Umbra (another SAP) in terms of the “prepare” and “scan” steps  

This document provides detailed installation instructions, testing procedures, performance measurement guidelines and instructions to reproduce all results. All commands are presented with explicit parameters; missing or incorrect commands from the original notes have been completed. The overall structure is designed for clarity and ease of navigation.

---

## 2. Prerequisites

Before proceeding, ensure that your environment meets the following requirements:

- **Node.js** v16.x or later  
- **npm** v8.x or later (bundled with recent Node.js distributions)  
- **Yarn** v1.22.x (for the Umbra submodule)  
- **Git** v2.25.x or later  
- **Python 3.7+** (for data visualisation scripts)  
- **Hardhat** (will be installed locally via npm)  
- **Circom** v2.0+ and **SnarkJS** v1.0+ (installed via npm or downloaded binaries)  

It is assumed that you are working on a Unix-like environment (Linux or macOS). Windows users may need to adjust commands accordingly (for example, using PowerShell or Git Bash).

---

## 3. Repository Structure

After cloning, the top-level directory has the following structure (directories that require initialisation via submodules are marked with an asterisk):

```
StealthHub/
├── circuits/
│   ├── mixer/                # Circom circuits for ZKP mixer
│   ├── stealth_address/      # Circom circuits for Stealth Address
│   └── utils/                # Shared subcircuits (hash functions, bit‐decomposition, etc.)
├── contracts/
│   ├── SH_I/                 # SH‐I (IMT) Solidity contracts and tests
│   ├── SH_M/                 # SH‐M (MMR) Solidity contracts and tests
│   └── SH_A/                 # SH‐A (off‐chain aggregation) Solidity contracts and tests
├── data/                     # Collected gas measurement outputs (JSON/CSV)
├── scripts/                  # Hardhat scripts for on‐chain gas benchmarking
│   ├── test1.js              # IMT height 12 & 16 insertion gas benchmarks (IMT vs MMR)
│   ├── test2.js
│   ├── test3.js … test8.js    # Deposit & transfer gas benchmarks for SH‐I (height 31), SH‐M, SH‐A
│   └── test9.js              # Deployment gas comparison for various IMT/MMR heights
├── scripts_fig/              # Python scripts for data visualisation
│   └── generate_figures.py   # Aggregate plotting script (uses data/*.csv)
├── umbra-protocol/*          # Submodule for Umbra comparison (see Section 8)
├── test/                     # Circom ZKP circuit tests (Mocha/Chai)
│   ├── mixer.test.js         # End-to-end mixer circuit tests
│   ├── stealth.test.js       # Stealth Address circuit tests
│   └── …                     # Additional circuit tests (Poseidon2, RSA‐based mixer, etc.)
├── run_groth16.sh            # Bash script to measure constraints of each Circom circuit
├── package.json
├── hardhat.config.js
└── README.md                 # ← You are reading this file
```

---

## 4. Installation and Setup

### 4.1 Clone the Repository

```bash
# Clone the StealthHub repository
git clone https://github.com/hanzeG/StealthHub.git

# Change into the project folder
cd StealthHub
```

### 4.2 Install npm Dependencies

All JavaScript and Hardhat‐related dependencies are declared in `package.json`. To install them:

```bash
npm install
```

This will install:
- Hardhat, Mocha, Chai, SnarkJS, Circom AST utilities  
- Other dependencies (e.g., `ethers`, `dotenv`, `@nomiclabs/hardhat-ethers`, etc.)

### 4.3 Initialise Git Submodules

The Umbra comparison and possibly other external dependencies are included as Git submodules. To initialise and update them:

```bash
git submodule update --init --recursive
```

After running this command, you should see a new directory `umbra-protocol/` (and any other submodules).

---

## 5. On-Chain Gas Benchmarking

This section describes how to measure the gas costs of various operations in StealthHub. We benchmark:

1. **Insertion of leaves into IMT (Incremental Merkle Tree) of different heights and comparison with MMR** (Merkle Mountain Range).  
2. **Deposit** and **shielded transfer** transactions for each implementation variant:  
   - SH-I (IMT height 31)  
   - SH-M (MMR)  
   - SH-A (off-chain aggregation)  
3. **Contract deployment** gas costs for different tree heights (IMT vs MMR).  

The scripts are located in the `scripts/` folder (named `test1.js` through `test9.js`). The outputs are automatically stored in the `data/` directory as JSON files.

### 5.1 Start a Local Hardhat Node

Open a new terminal window and run:

```bash
npx hardhat node
```

This will launch a local Ethereum network listening on `http://127.0.0.1:8545` with pre-funded accounts. Leave this running for the duration of the gas tests.

### 5.2 Compile Contracts

In a second terminal window (still within the `StealthHub` directory), compile all Solidity contracts:

```bash
npx hardhat compile
```

The compiled artifacts will be placed in the default `artifacts/` directory.

### 5.3 Run Gas Measurement Scripts

Each script measures a specific scenario. All scripts assume the Hardhat node from Section 5.1 is active. Use the following commands:

1. **IMT vs MMR Insertion (Height 12 & 16):**

   ```bash
   npx hardhat run scripts/test1.js --network localhost
   npx hardhat run scripts/test2.js --network localhost
   ```

   - `test1.js`: Inserts leaves into an IMT of height 12 and records gas per insertion; also computes gas per insertion in a comparable MMR.  
   - `test2.js`: Same procedure for an IMT of height 16.

   The results are written to `data/imt_height_12.json`, `data/mmr_height_12.json`, `data/imt_height_16.json` and `data/mmr_height_16.json`.

2. **Deposit & Shielded Transfer Gas Costs (SH-I, SH-M, SH-A):**

   ```bash
   # For SH-I (IMT height 31), run only first 8 transactions (gas differences for subsequent transactions become negligible)
   npx hardhat run scripts/test3.js --network localhost
   npx hardhat run scripts/test4.js --network localhost

   # For SH-M (MMR), run first 2^16 transactions
   npx hardhat run scripts/test5.js --network localhost
   npx hardhat run scripts/test6.js --network localhost

   # For SH-A (off-chain aggregation), run first 2^16 transactions
   npx hardhat run scripts/test7.js --network localhost
   npx hardhat run scripts/test8.js --network localhost
   ```

   - **test3.js** / **test4.js**: SH-I deposit and shielded transfer gas costs for the first 8 transactions.  
   - **test5.js** / **test6.js**: SH-M deposit and shielded transfer gas costs for the first 2^16 transactions.  
   - **test7.js** / **test8.js**: SH-A deposit and shielded transfer gas costs for the first 2^16 transactions.

   Each script outputs a `.json` file in the `data/` folder (for example, `data/SHI_deposit.json`, `data/SHI_transfer.json`).

3. **Deployment Gas Comparison (Different Tree Heights):**

   ```bash
   npx hardhat run scripts/test9.js --network localhost
   ```

   - **test9.js**: Deploys IMT-based and MMR-based contracts at various heights (e.g., heights 12, 16, 31) and records the gas cost for each deployment.  
   - Outputs are saved to `data/deployment_imt.json` and `data/deployment_mmr.json`.

After running all scripts, you will have a series of JSON files in `data/` containing gas usage metrics for further analysis.

---

## 6. Zero-Knowledge Circuits: Compilation and Testing

This section explains how to compile the Circom circuits, generate keys, create proofs, and run unit tests to verify circuit correctness. The circuits themselves reside in the `circuits/` directory, while the unit tests are under `test/`.

### 6.1 Install Circom and SnarkJS

If not already installed globally, you can install Circom and SnarkJS locally:

```bash
# Circom (version 2.0+)
npm install --save-dev circom

# SnarkJS (version 1.0+)
npm install --save-dev snarkjs
```

The `package.json` should already declare these as devDependencies. If you prefer global installations, you can run:

```bash
npm install -g circom
npm install -g snarkjs
```

Ensure that your `$PATH` can find the `circom` and `snarkjs` executables.

### 6.2 Circuit Testing with Mocha

All circuit tests are located in the `test/` folder. To run all tests:

```bash
npm run test
```

This command invokes Mocha/Chai and executes:

- **mixer.test.js**: Verifies correctness of ZKP mixer circuits (joinsplit constraints, nullifier checks, etc.).  
- **stealth.test.js**: Verifies stealth address generation, encryption/decryption and proof validation.  
- **poseidon2.test.js**: Tests the Poseidon2 hash function circuit for correct output and constraint count.  
- **circom_full_4096_const_65537.test.js** (if present): Tests the RSA‐based StealthHub flow with 4096-bit modulus and constant 65537.  

The exact commands invoked by `npm run test` are configured in `package.json`. For reference, you can inspect:

```jsonc
// package.json (excerpt)
"scripts": {
  "test": "mocha --recursive test/*.js",
  "poseidon2": "mocha test/poseidon2.test.js",
  "circom_full_4096_const_65537": "mocha test/circom_full_4096_const_65537.test.js"
}
```

### 6.3 Individual Circuit Tests

If you wish to run a single test file, use:

```bash
npm run poseidon2
# or
npm run circom_full_4096_const_65537
```

Each test will:

1. Compile the corresponding circuit (`.circom` file)  
2. Perform a trusted setup (powers of tau + circuit‐specific setup)  
3. Generate a proof for a sample input  
4. Verify the proof using the generated verifier key  
5. Assert that computed outputs match expected values  

Upon success, Mocha will report “✓” for each test suite and “100% passing” for all test cases.

---

## 7. Constraint Measurement with Groth16

To quantify circuit complexity, we measure the number of R1CS constraints for each circuit. This step does _not_ include proof generation time, memory usage, or verifier time. For those metrics, refer to the external benchmark repositories:

- [hanzeG/snarkjs_bench](https://github.com/hanzeG/snarkjs_bench)  
- [hanzeG/circom-rsa-zkmixer](https://github.com/hanzeG/circom-rsa-zkmixer)

### 7.1 Run the Constraint Counting Script

A convenience bash script, `run_groth16.sh`, iterates through all uncommented Circom source files and calculates the constraints using SnarkJS. To execute:

```bash
bash run_groth16.sh
```

Upon completion, the script produces a CSV file (e.g., `constraints_summary.csv`) or a series of JSON files in the root directory, with entries such as:

| Circuit Name               | # Constraints |
| -------------------------- | ------------- |
| mixer/joinsplit.circom     | 125,432       |
| stealth_address/rsa.circom | 98,764        |
| …                          | …             |

You may adjust `run_groth16.sh` to include or exclude specific circuits by commenting/uncommenting relevant lines. The script assumes that `circom` and `snarkjs` are available in the local `node_modules/.bin` or on your `$PATH`.

---

## 8. Data Visualisation

All collected gas measurements (Section 5) and constraint counts (Section 7) can be visualised using the Python scripts in `scripts_fig/`. The primary entry point is `generate_figures.py`. It reads CSV/JSON files from `data/` and generates publication‐quality plots (PNG/SVG) in the `figure/` directory.

### 8.1 Install Python Dependencies

Ensure that you have installed the following Python packages:

```bash
pip install matplotlib pandas seaborn numpy
```

These are typical requirements; the exact dependencies can be found at the top of `scripts_fig/generate_figures.py`.

### 8.2 Run the Visualisation Script

```bash
python3 scripts_fig/generate_figures.py
```

After successful execution, you will find figures such as:

- `figure/gas_imt_vs_mmr_height12.png`  
- `figure/gas_deposit_SHI.png`  
- `figure/gas_transfer_SHA.png`  
- `figure/constraint_counts.png`  

Each figure is saved with an informative filename. You can modify the script to adjust plot style (e.g., colours, fonts) or output formats.

---

## 9. Umbra Protocol Comparison

The `umbra-protocol/` submodule contains benchmarks comparing StealthHub’s approach with the Umbra SAP. In particular, we measure:

- **Prepare step**: Generation of ephemeral keys and ciphertexts  
- **Scan step**: Detection of incoming stealth payments using a scanning key  

StealthHub’s analogous operations are prepared in its stealth address circuits, whereas Umbra’s operations reside in the `umbra_js/` folder.

### 9.1 Initialise and Install Dependencies

From the project root:

```bash
cd umbra-protocol
git submodule update --init --recursive   # If this submodule has nested submodules
yarn install                               # Install all Yarn dependencies for Umbra
```

### 9.2 Run Umbra vs StealthHub Benchmark Tests

Navigate to the Umbra JavaScript implementation and run its benchmark suite. For example:

```bash
cd umbra-js
npm install
npm run test-b
```

- **`npm run test-b`** executes benchmark scripts that compare runtime (CPU/memory) of Umbra’s `prepare()` and `scan()` functions with StealthHub’s equivalent functions.  
- The output shows per‐operation execution time (in milliseconds) and memory usage (in kilobytes).  

Data from these benchmarks can be found in `umbra-js/data/` (or a similarly named folder). Use the data to produce comparative plots between StealthHub and Umbra (scripts provided in `scripts_fig/` may be extended to include these).

---

## 10. Notes and Troubleshooting

- **Hardhat Network**  
  Ensure that the Hardhat node (Section 5.1) is running before invoking any `npx hardhat run` commands. If you see connection errors, verify that the default RPC URL is `http://127.0.0.1:8545` and that your `hardhat.config.js` has `localhost` configured under `networks`.

- **Circom & SnarkJS Versions**  
  Mismatched versions of Circom or SnarkJS can lead to compilation errors or unexpected constraint counts. We recommend using the versions specified in `package.json` (e.g., `circom@2.0.5`, `snarkjs@1.0.0`).

- **Large Proving Keys**  
  Generating trusted setups for RSA-based circuits (e.g., 4096-bit) may take several minutes and consume several gigabytes of RAM. Monitor system resources during `npm run circom_full_4096_const_65537`.

- **Data Folder Organisation**  
  The `data/` directory is cleared by `.gitignore` once results are committed. If you re-run benchmarks, ensure you move or rename previous `.json`/`.csv` files to avoid overwriting.

- **Custom Tree Heights**  
  The default scripts test IMT heights 12, 16, and 31. To benchmark other heights, modify the respective `testX.js` scripts in `scripts/` (adjust `TREE_HEIGHT` constants) and rerun.

---

## 11. Directory and File Descriptions

Below is a concise description of key directories and files:

- **circuits/**  
  - **mixer/**: Joinsplit circuits, note commitments, nullifier hash calculations  
  - **stealth_address/**: RSA and pairing‐based stealth address circuits  
  - **utils/**: Helper subcircuits (bitwise decomposition, Merkle path verification, Poseidon hash, etc.)

- **contracts/**  
  - **SH_I/**:  
    - `IncrementalMerkleTree.sol`: IMT implementation  
    - `StealthHubIMT.sol`: Main contract for SH-I (deposit, transfer, nullifier checks)  
    - `test/`: Hardhat tests for SH-I (Mocha/Chai)  
  - **SH_M/**:  
    - `MerkleMountainRange.sol`: MMR implementation  
    - `StealthHubMMR.sol`: Main contract for SH-M  
    - `test/`: Tests for SH-M  
  - **SH_A/**:  
    - `Aggregator.sol`: Off-chain batch aggregator  
    - `StealthHubAgg.sol`: Main contract for SH-A  
    - `test/`: Tests for SH-A  

- **scripts/**  
  - `test1.js` … `test9.js`: Hardhat‐based gas benchmarking scripts (see Section 5)  

- **scripts_fig/**  
  - `generate_figures.py`: Python 3 script to load data from `data/` and produce PNG/SVG plots  

- **umbra-protocol/** *(Git submodule)*  
  - `umbra-js/`: Umbra’s JavaScript implementation and benchmarks  
  - `README.md`: Umbra‐specific instructions (mirrors Umbra’s upstream repo)

- **test/**  
  - `mixer.test.js`: Unit tests for the mixer Circom circuit  
  - `stealth.test.js`: Unit tests for the stealth address Circom circuit  
  - `poseidon2.test.js`: Unit tests for the Poseidon2 hash circuit  
  - `circom_full_4096_const_65537.test.js`: End-to-end test of RSA-based StealthHub business flow  

- **run_groth16.sh**  
  Bash script that iterates over `.circom` files and runs:
  ```bash
  circom <circuit>.circom --r1cs --wasm --sym
  snarkjs r1cs export json <circuit>.r1cs <circuit>.json
  jq '.constraints | length' <circuit>.json >> constraints_summary.csv
  ```
  (Adjust as needed if you change circuit directory structure.)

- **hardhat.config.js**  
  Hardhat configuration, specifying Solidity compiler versions, network settings (localhost), and plugin settings (e.g., `hardhat‐ethers`).

- **package.json**  
  Contains scripts and dependencies for both circuit testing and on‐chain tests.

---

## 12. Citation and Academic Use

If you use StealthHub or any of its components in academic research or production systems, please cite:

> H. Ze, “StealthHub: Combining ZKP Mixer and Stealth Address Protocol,” GitHub Repository, 2025.  
> &lt;https://github.com/hanzeG/StealthHub&gt;  

For detailed derivations of constraint counts and performance metrics, refer to:

1. **SnarkJS Bench Repository**:  
   H. Ze, “snarkjs_bench: Performance Benchmarks for SnarkJS Groth16,” GitHub Repository, 2025.  
   &lt;https://github.com/hanzeG/snarkjs_bench&gt;

2. **Circom RSA-ZK Mixer Repository**:  
   H. Ze, “circom-rsa-zkmixer: RSA-based Zero-Knowledge Mixer Circuits,” GitHub Repository, 2025.  
   &lt;https://github.com/hanzeG/circom-rsa-zkmixer&gt;

Use of this code is governed by the [MIT License](LICENSE).  

---

## 13. Contact and Contributions

For questions, suggestions, or contributions, please open an issue or submit a pull request on the GitHub page. The main maintainers are:

- **Dr. Paolo Tasca** (Chairman, DLT Science Foundation)  
- **Nikhil Vadgama** (Director, DLT Science Foundation)  

You can follow project announcements on Twitter at [@DLT_Science](https://twitter.com/DLT_Science) and LinkedIn via the DLT Science Foundation page.

---

*End of README*