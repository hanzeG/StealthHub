# StealthHub: A UTXO-Based Stealth Address Protocol

This repository presents **StealthHub**, a protocol combining Zero-Knowledge Proof (ZKP) based mixers and the Stealth Address Protocol (SAP). The system comprises:

- **Circom-based ZKP implementations**: ZK circuits developed in Circom for Poseidon2 hash functions, UTXO circuits using the Groth16 proving system (SnarkJS) and encryption/ decryption circuits for RSA-based constructions.
- **JavaScript unit tests**: A test suite (Mocha/Chai) that verifies circuit correctness, as well as end-to-end deposit and withdrawal operations across different implementations.
- **SnarkJS Groth16 performance scripts**: Scripts that measure R1CS constraints (note that proving time, verifier time, and memory measurements (refer to `Figure 12` in the preprint) are provided in external benchmark repositories: [hanzeG/snarkjs_bench](https://github.com/hanzeG/snarkjs_bench).
- **On-chain smart contract implementations**:
  - **SH-I**: Incremental Merkle Tree (IMT) – based implementation
  - **SH-M**: Merkle Mountain Range (MMR) – based implementation
  - **SH-A**: Off-chain aggregation (batching) – based implementation
- **Chain-level test scripts**: Hardhat scripts that deploy and benchmark each variant’s smart contracts, collecting gas metrics for various operations.
- **Data visualisation**: Python scripts to generate publication-quality plots from gas and constraint data.

---

## 1. Installation and Setup

### 1.1 Preparation

1. Download Circom following the instructions at [installing Circom](https://docs.circom.io/getting-started/installation/).

2. Download SnarkJS: `npm install -g snarkjs`

### 1.2 Clone the Repository

Clone the StealthHub repository and install JavaScript dependencies:

Clone the StealthHub repository

```bash
git clone https://github.com/hanzeG/StealthHub.git
```

Change into the project folder and install all npm dependencies (Mocha, Chai, etc.)

```bash
cd StealthHub && npm install
```

### 1.3 Initialise Git Submodules

Some components require external repositories (for example, the Umbra comparison). To initialise and update all submodules, run:

```bash
git submodule update --init --recursive
```

After this command, you should see a new directory `umbra-protocol/` (and any other submodules) populated with its own files.

### 1.4 Initialise Submodule Dependencies

After updating all submodules, each submodule has its own dependencies that must be installed. Perform the following steps:

1. **Umbra Submodule**  

    Please run all these commands from the umbra-protocol workspace root and edit the .env with your own environment variable values.

    ```bash
    cd umbra-protocol && cp contracts-core/.env.example contracts-core/.env
    ```

    ```dotenv
    MNEMONIC=here is where your twelve words mnemonic should be put my friend
    DEPLOY_GSN=false
    ETHERSCAN_VERIFICATION_API_KEY="YOUR_API_KEY"
    BASE_RPC_URL=
    ```

    ```bash 
    yarn install
    ```
    
    ```bash
    cd umbra-js && cp umbra-js/.env.example umbra-js/.env
    ```

    ```dotenv
    cat << 'EOF' > .env
    ETHERSCAN_API_KEY=yourEtherscanApiKey
    OPTIMISTIC_ETHERSCAN_API_KEY=yourOptimisticEtherscanApiKey
    POLYGONSCAN_API_KEY=yourPolygonscanApiKey
    ARBISCAN_API_KEY=yourArbiscanApiKey
    GNOSISSCAN_API_KEY=yourGnosisSafeScanApiKey
    MAINNET_RPC_URL=yourMainnetRpcUrl
    OPTIMISM_RPC_URL=yourOptimismRpcUrl
    GNOSIS_CHAIN_RPC_URL=yourGnosisChainRpcUrl
    POLYGON_RPC_URL=yourPolygonRpcUrl
    ARBITRUM_ONE_RPC_URL=yourArbitrumOneRpcUrl
    SEPOLIA_RPC_URL=yourSepoliaRpcUrl
    BASE_RPC_URL=yourBaseRpcUrl
    EOF
    ```
    
    ```bash
    npm install
    ```

2. **CircomLib**  
   
    ```bash
    cd ../circom-ecdsa && npm install
    ```

---

## 2. On-Chain Gas Benchmarking

This section describes how to measure on-chain gas costs for various operations in StealthHub. All gas metrics will be saved as JSON or CSV in the `data/` directory.

### 2.1 Start a Local Hardhat Node

Open one terminal and launch a local Hardhat network:

```bash
npx hardhat node
```

This will spawn a local Ethereum node at `http://127.0.0.1:8545` with pre-funded accounts. Keep this running for the duration of the gas tests.

### 2.2 Compile Contracts

In a second terminal (still within the `StealthHub` directory), compile all Solidity contracts:

```bash
npx hardhat compile
```

Compiled artifacts appear under `artifacts/` by default.

### 2.3 Run Gas Measurement Scripts

Each script under `scripts/` benchmarks a specific scenario. All scripts assume the Hardhat node from Section 2.1 is active. The results are written to the `data/` directory.

1. **IMT vs MMR Insertion (Heights 12 & 16):**

    Height 12

    ```bash
    npx hardhat run scripts/test1.js --network localhost
    ```

    Height 16

    ```bash
    npx hardhat run scripts/test2.js --network localhost
    ```

    - `test1.js`: Inserts leaves into an IMT of height 12, recording gas per insertion; also computes gas per insertion in a comparable MMR of height 12.  
    - `test2.js`: Same procedure for an IMT of height 16 and its corresponding MMR.  
    - Please refer to `Figure 13` in the preprint.

2. **Deposit & Shielded Transfer Gas Costs (SH-I, SH-M, SH-A):**

    SH-I (StealthHub base on IMT, IMT height 31, record first 8 transactions)
    
    ```bash
    # deposit
    npx hardhat run scripts/test3.js --network localhost
    ```
    ```bash
    # shielded transfer
    npx hardhat run scripts/test4.js --network localhost
    ```
    
    SH-M (StealthHub base on MMR, record first 2^16 transactions)

    ```bash
    # deposit
    npx hardhat run scripts/test5.js --network localhost
    ```
    ```bash
    # shielded transfer
    npx hardhat run scripts/test6.js --network localhost
    ```

    SH-A (StealthHub base on off-chain aggregation and MMR, record first 2^16 transactions)
    
    ```bash
    # deposit
    npx hardhat run scripts/test7.js --network localhost
    ```
    ```bash
    # shielded transfer
    npx hardhat run scripts/test8.js --network localhost
    ```

    - **test3.js** / **test4.js**: SH-I deposit and shielded transfer gas costs for the first 8 transactions (differences become negligible after initial deposits in an IMT of height 31).  
    - **test5.js** / **test6.js**: SH-M deposit and shielded transfer gas costs for the first 2^16 transactions.  
    - **test7.js** / **test8.js**: SH-A deposit and shielded transfer gas costs for the first 2^16 transactions.  
    - See the results above in `Figure 14` and `Table 3` in the preprint.

3. **Deployment Gas Comparison (Various Tree Heights):**

    ```bash
    npx hardhat run scripts/test9.js --network localhost
    ```

    - **test9.js**: Deploys IMT-based and MMR-based contracts at heights 12, 16 and 31, recording the gas cost for each deployment.
    - In the prerint (see `Table 2`), we deployed these contracts on testnet directily, please refer to the transactions on BNB Testnet below:
      - IMT height 31: [`0x49b8c1af615fea62875aa3813c3da73a7c19bd9011934b8233ff535bfd6e2df3`](https://testnet.bscscan.com/tx/0x49b8c1af615fea62875aa3813c3da73a7c19bd9011934b8233ff535bfd6e2df3)
      - IMT height 16: [`0xa5c11b65d96ebb0e182124bcd1cadfe317f5da95f1ea620bc21de9f5b5094fb3`](https://testnet.bscscan.com/tx/0xa5c11b65d96ebb0e182124bcd1cadfe317f5da95f1ea620bc21de9f5b5094fb3)
      - IMT height 8: [`0xbf408dae681334b7797d9c2b78391bb141f881bf5208ebe9df40c0cd988036a3`](https://testnet.bscscan.com/tx/0xbf408dae681334b7797d9c2b78391bb141f881bf5208ebe9df40c0cd988036a3)
      - IMT height 4: [`0x7b7848bea39423d8ce8ad813b1bf3b4c135e1fe68e539c256c610601b127401a`](https://testnet.bscscan.com/tx/0x7b7848bea39423d8ce8ad813b1bf3b4c135e1fe68e539c256c610601b127401a)
      - MMR: [`0xe0ae9482bbea237964e11c73f67d09dcd720c9608158e95dd64f44cb74580444`](https://testnet.bscscan.com/tx/0xe0ae9482bbea237964e11c73f67d09dcd720c9608158e95dd64f44cb74580444)

---

## 3. Zero-Knowledge Circuit Testing

All Circom circuit tests reside in the `test/` directory. Test instructions are defined in `package.json`.

**Run All Tests**

```bash
npm run test
```

This executes Mocha/Chai over all files in `test/`, including:  
   - `poseidon2.test.js`: Validates the Poseidon2 hash function circuit.  
   - `circom_multi_mt.test.js`: Validate the nested Merkle tree (on-chain tree + off-chain tree) funtions. 
   - `circom_full_1024_const_65537.test.js`: End-to-end test of RSA-based StealthHub flow with a 1024-bit modulus and exponent 65537.
   - `circom_full_2048_const_65537.test.js`: ... with a 2048-bit modulus and exponent 65537.
   - `circom_full_4096_const_65537.test.js`: ... with a 4096-bit modulus and exponent 65537.
   - `circom_mod_pow.test.js`: Validate the large integer exponentiation functionality (not used in StealthHub, but potentially useful for RSA accumulators). 

Each test suite compiles the corresponding circuit, checks that computed outputs match expected values. Successful tests will result in Mocha reporting “✓” for each suite and “100% passing” overall.

---

## 4. Constraint Measurement with Groth16

To quantify circuit complexity, measure the number of R1CS constraints for each circuit. This step does _not_ include proof generation time, memory usage or verifier time. External benchmark repositories provide those additional metrics:

- [hanzeG/snarkjs_bench](https://github.com/hanzeG/snarkjs_bench)  
- [hanzeG/circom-rsa-zkmixer](https://github.com/hanzeG/circom-rsa-zkmixer)

A convenience script, `run_groth16.sh`, iterates through all uncommented `.circom` files and calculates the constraint count using SnarkJS:

```bash
bash run_groth16.sh
```

You may modify `run_groth16.sh` to include or exclude specific circuits by commenting or uncommenting relevant lines. The script assumes that `circom` and `snarkjs` executables are available either in `node_modules/.bin` or on your system PATH. See the results above in `Figure 11` in the preprint.

---

## 5. Data Visualisation

All collected gas measurements (Section 2), constraint counts (Section 4), and sorted ZKP metrics (external benchmark repositories) can be visualised using Python scripts in `scripts_fig/`. It reads JSON files from `data/` and generates publication-quality plots in `figure/`.

### 5.1 Install Python Dependencies

Ensure that you have installed the following packages:

```bash
pip install matplotlib pandas seaborn numpy
```

The exact dependencies can be found at the top of `scripts_fig/<script-name>`.

### 5.2 Run the Visualisation Script

```bash
python3 scripts_fig/<script-name>
```

---

## 6. Umbra Protocol Comparison

The `umbra-protocol/` submodule contains benchmarks comparing StealthHub’s prepare and scan operations with those of the Umbra SAP. To reproduce this comparison:

**Run Umbra vs StealthHub Benchmark Tests**

```bash
npm run test-b
```

This command installs all Yarn dependencies required by the Umbra comparison. The script `test-b` executes benchmark routines comparing the runtime of Umbra’s `prepare()` and `scan()` functions for the "announcements" with StealthHub’s analogous operations. Please refer to `Table 1` in the preprint.