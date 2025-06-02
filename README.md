# StealthHub: A UTXO-Based Stealth Address Protocol

## 1. Introduction

StealthHub is a protocol that combines a zero-knowledge proof (ZKP) mixer with a Stealth Address Protocol (SAP) to enhance transaction privacy and unlinkability on blockchain networks. The core components of this repository include:

- **Circom-based ZKP implementations**: Circuits developed in Circom for Pedersen and Poseidon hash functions, mixer circuits using the Groth16 proving system (SnarkJS) and stealth address circuits for both RSA-based and pairing-based constructions.
- **JavaScript unit tests**: A test suite (Mocha/Chai) that verifies circuit correctness, as well as end-to-end deposit and withdrawal operations across different implementations.
- **SnarkJS Groth16 performance scripts**: Scripts that measure R1CS constraints, proving time and verifier time (note that memory measurements are provided in external benchmark repositories).
- **On-chain smart contract implementations**:
  - **SH-I**: Incremental Merkle Tree (IMT) – based implementation
  - **SH-M**: Merkle Mountain Range (MMR) – based implementation
  - **SH-A**: Off-chain aggregation (batching) – based implementation
- **Chain-level test scripts**: Hardhat scripts that deploy and benchmark each variant’s smart contracts, collecting gas metrics for various operations.
- **Data visualisation**: Python scripts to generate publication-quality plots from gas and constraint data.

The remainder of this document provides detailed installation instructions, testing procedures, performance measurement guidelines and instructions to reproduce all results. Each section offers explicit commands and contextual explanations.

---

## 2. Repository Structure

After cloning, the repository has the following structure (directories requiring submodule initialisation are marked with an asterisk):

```
StealthHub/
├── circuits/
│   ├── mixer/                # Circom circuits for ZKP mixer (joinsplit, nullifiers, commitments)
│   ├── stealth_address/      # Circom circuits for stealth address (RSA and pairing-based)
│   └── utils/                # Shared subcircuits (hash functions, bit decomposition, Merkle proof)
├── contracts/
│   ├── SH_I/                 # SH-I (IMT) Solidity contracts and tests
│   ├── SH_M/                 # SH-M (MMR) Solidity contracts and tests
│   └── SH_A/                 # SH-A (off-chain aggregation) Solidity contracts and tests
├── data/                     # Collected gas measurement outputs (JSON/CSV)
├── scripts/                  # Hardhat scripts for on-chain gas benchmarking
│   ├── test1.js              # IMT (height 12) vs MMR insertion gas benchmarks
│   ├── test2.js              # IMT (height 16) vs MMR insertion gas benchmarks
│   ├── test3.js … test8.js   # Deposit and shielded transfer benchmarks for SH-I, SH-M, SH-A
│   └── test9.js              # Deployment gas comparison across different tree heights
├── scripts_fig/              # Python scripts for data visualisation
│   └── generate_figures.py   # Aggregate plotting script (reads data/*.csv, outputs figure/)
├── umbra-protocol/*          # Submodule for Umbra comparison (prepare and scan steps)
├── test/                     # Circom ZKP circuit tests (Mocha/Chai)
│   ├── mixer.test.js         # Mixer circuit end-to-end tests
│   ├── stealth.test.js       # Stealth address circuit tests
│   ├── poseidon2.test.js     # Poseidon2 hash function circuit tests
│   └── circom_full_4096_const_65537.test.js # RSA-based StealthHub end-to-end flow
├── run_groth16.sh            # Bash script to measure R1CS constraints for all Circom circuits
├── package.json              # NPM scripts and dependencies
├── hardhat.config.js         # Hardhat configuration (Solidity versions, networks, plugins)
└── README.md                 # ← This file (updated to reflect academic style and structure)
```

---

## 3. Prerequisites

Before proceeding, ensure that your environment meets the following requirements:

- **Node.js** v16.x or later  
- **npm** v8.x or later (bundled with recent Node.js versions)  
- **Yarn** v1.22.x (for the Umbra submodule)  
- **Git** v2.25.x or later  
- **Python 3.7+** (for data visualisation scripts)  
- **Hardhat** (installed locally via npm)  
- **Circom** v2.0+ (installed via npm)  
- **SnarkJS** v1.0+ (installed via npm)  

It is assumed that you are working on a Unix-like environment (Linux or macOS). Windows users may need to adjust commands (e.g. via PowerShell or Git Bash).

---

## 4. Installation and Setup

### 4.1 Clone the Repository

Clone the StealthHub repository and install JavaScript dependencies:

```bash
# Clone the StealthHub repository
git clone https://github.com/hanzeG/StealthHub.git

# Change into the project folder
cd StealthHub

# Install all npm dependencies (Hardhat, Mocha, Chai, SnarkJS, Circom, etc.)
npm install
```

### 4.2 Initialise Git Submodules

Some components require external repositories (for example, the Umbra comparison). To initialise and update all submodules, run:

```bash
git submodule update --init --recursive
```

After this command, you should see a new directory `umbra-protocol/` (and any other submodules) populated with its own files.

---

## 5. On-Chain Gas Benchmarking

This section describes how to measure on-chain gas costs for various operations in StealthHub. All gas metrics will be saved as JSON or CSV in the `data/` directory.

### 5.1 Start a Local Hardhat Node

Open one terminal and launch a local Hardhat network:

```bash
npx hardhat node
```

This will spawn a local Ethereum node at `http://127.0.0.1:8545` with pre-funded accounts. Keep this running for the duration of the gas tests.

### 5.2 Compile Contracts

In a second terminal (still within the `StealthHub` directory), compile all Solidity contracts:

```bash
npx hardhat compile
```

Compiled artifacts appear under `artifacts/` by default.

### 5.3 Run Gas Measurement Scripts

Each script under `scripts/` benchmarks a specific scenario. All scripts assume the Hardhat node from Section 5.1 is active. The results are written to the `data/` directory.

1. **IMT vs MMR Insertion (Heights 12 & 16):**

   ```bash
   # Height 12
   npx hardhat run scripts/test1.js --network localhost
   # Height 16
   npx hardhat run scripts/test2.js --network localhost
   ```

   - `test1.js`: Inserts leaves into an IMT of height 12, recording gas per insertion; also computes gas per insertion in a comparable MMR of height 12.  
   - `test2.js`: Same procedure for an IMT of height 16 and its corresponding MMR.  
   - Outputs:  
     - `data/imt_height_12.json`  
     - `data/mmr_height_12.json`  
     - `data/imt_height_16.json`  
     - `data/mmr_height_16.json`

2. **Deposit & Shielded Transfer Gas Costs (SH-I, SH-M, SH-A):**

   ```bash
   # SH-I (IMT height 31, record first 8 transactions)
   npx hardhat run scripts/test3.js --network localhost
   npx hardhat run scripts/test4.js --network localhost

   # SH-M (MMR, record first 2^16 transactions)
   npx hardhat run scripts/test5.js --network localhost
   npx hardhat run scripts/test6.js --network localhost

   # SH-A (Off-chain aggregation, record first 2^16 transactions)
   npx hardhat run scripts/test7.js --network localhost
   npx hardhat run scripts/test8.js --network localhost
   ```

   - **test3.js** / **test4.js**: SH-I deposit and shielded transfer gas costs for the first 8 transactions (differences become negligible after initial deposits in an IMT of height 31).  
   - **test5.js** / **test6.js**: SH-M deposit and shielded transfer gas costs for the first 2^16 transactions.  
   - **test7.js** / **test8.js**: SH-A deposit and shielded transfer gas costs for the first 2^16 transactions.  
   - Outputs (examples):  
     - `data/SHI_deposit.json`, `data/SHI_transfer.json`  
     - `data/SHM_deposit.json`, `data/SHM_transfer.json`  
     - `data/SHA_deposit.json`, `data/SHA_transfer.json`

3. **Deployment Gas Comparison (Various Tree Heights):**

   ```bash
   npx hardhat run scripts/test9.js --network localhost
   ```

   - **test9.js**: Deploys IMT-based and MMR-based contracts at heights 12, 16 and 31, recording the gas cost for each deployment.  
   - Outputs:  
     - `data/deployment_imt.json`  
     - `data/deployment_mmr.json`

---

## 6. Zero-Knowledge Circuit Testing

All Circom circuit tests reside in the `test/` directory. Test instructions are defined in `package.json`. The following commands illustrate typical workflows:

1. **Run All Tests**

   ```bash
   npm run test
   ```

   This executes Mocha/Chai over all files in `test/`, including:  
   - `mixer.test.js`: Verifies mixer circuit functionality (joinsplit constraints, nullifier checks).  
   - `stealth.test.js`: Verifies stealth address generation, encryption/decryption and proof validation.  
   - `poseidon2.test.js`: Validates the Poseidon2 hash function circuit.  
   - `circom_full_4096_const_65537.test.js`: End-to-end test of RSA-based StealthHub flow with a 4096-bit modulus and exponent 65537.

2. **Run Poseidon2-Only Test**

   ```bash
   npm run poseidon2
   ```

3. **Run RSA-Based StealthHub Flow Test**

   ```bash
   npm run circom_full_4096_const_65537
   ```

Each test suite compiles the corresponding circuit, performs a trusted setup (powers-of-tau + circuit-specific setup), generates a proof for a sample input, verifies the proof, and checks that computed outputs match expected values. Successful tests will result in Mocha reporting “✓” for each suite and “100% passing” overall.

---

## 7. Constraint Measurement with Groth16

To quantify circuit complexity, measure the number of R1CS constraints for each circuit. This step does _not_ include proof generation time, memory usage or verifier time. External benchmark repositories provide those additional metrics:

- [hanzeG/snarkjs_bench](https://github.com/hanzeG/snarkjs_bench)  
- [hanzeG/circom-rsa-zkmixer](https://github.com/hanzeG/circom-rsa-zkmixer)

### 7.1 Run the Constraint Counting Script

A convenience script, `run_groth16.sh`, iterates through all uncommented `.circom` files and calculates the constraint count using SnarkJS:

```bash
bash run_groth16.sh
```

Upon completion, the script produces a CSV file `constraints_summary.csv` or a series of JSON summaries in the root directory, typically containing entries such as:

| Circuit Name                 | # Constraints |
| ---------------------------- | ------------- |
| `mixer/joinsplit.circom`     | 125 432       |
| `stealth_address/rsa.circom` | 98 764        |
| …                            | …             |

You may modify `run_groth16.sh` to include or exclude specific circuits by commenting or uncommenting relevant lines. The script assumes that `circom` and `snarkjs` executables are available either in `node_modules/.bin` or on your system PATH.

---

## 8. Data Visualisation

All collected gas measurements (Section 5) and constraint counts (Section 7) can be visualised using Python scripts in `scripts_fig/`. The primary entry point is `generate_figures.py`. It reads CSV/JSON files from `data/` and generates publication-quality plots in `figure/`.

### 8.1 Install Python Dependencies

Ensure that you have installed the following packages:

```bash
pip install matplotlib pandas seaborn numpy
```

The exact dependencies can be found at the top of `scripts_fig/generate_figures.py`.

### 8.2 Run the Visualisation Script

```bash
python3 scripts_fig/generate_figures.py
```

After successful execution, you will find figures such as:

- `figure/gas_imt_vs_mmr_height12.png`  
- `figure/gas_deposit_SHI.png`  
- `figure/gas_transfer_SHA.png`  
- `figure/constraint_counts.png`  

Each figure is saved with a descriptive filename. You may modify the script to adjust plot styles (e.g. colours, fonts) or output formats as needed.

---

## 9. Umbra Protocol Comparison

The `umbra-protocol/` submodule contains benchmarks comparing StealthHub’s prepare and scan operations with those of the Umbra SAP. To reproduce this comparison:

1. **Initialise and Install Dependencies**

   ```bash
   cd umbra-protocol
   yarn install
   ```

2. **Run Umbra vs StealthHub Benchmark Tests**

   ```bash
   cd umbra-js
   npm install
   npm run test-b
   ```

   - The script `test-b` executes benchmark routines comparing the runtime (CPU, memory) of Umbra’s `prepare()` and `scan()` functions with StealthHub’s analogous operations.  
   - Output data (e.g. execution time in milliseconds, memory usage in kilobytes) can be found under `umbra-js/data/` and may be incorporated into the plots in `scripts_fig/`.
```