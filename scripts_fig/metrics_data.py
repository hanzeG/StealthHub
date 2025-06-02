import json
import os

# Generate JSON data file
data = {
    "MiMC": [
        {"height":1,"setup_runtime":2.65,"prove_runtime":0.55,"setup_ram_MB":180.58,"prove_ram_MB":227.23},
        {"height":2,"setup_runtime":6.62,"prove_runtime":0.82,"setup_ram_MB":211.80,"prove_ram_MB":314.63},
        {"height":3,"setup_runtime":14.47,"prove_runtime":1.34,"setup_ram_MB":267.28,"prove_ram_MB":385.44},
        {"height":4,"setup_runtime":21.68,"prove_runtime":2.13,"setup_ram_MB":346.46,"prove_ram_MB":380.04},
        {"height":5,"setup_runtime":28.04,"prove_runtime":3.73,"setup_ram_MB":499.77,"prove_ram_MB":387.83},
        {"height":6,"setup_runtime":36.99,"prove_runtime":6.97,"setup_ram_MB":753.23,"prove_ram_MB":593.01},
        {"height":7,"setup_runtime":50.49,"prove_runtime":13.37,"setup_ram_MB":1130.24,"prove_ram_MB":906.41},
        {"height":8,"setup_runtime":93.86,"prove_runtime":26.15,"setup_ram_MB":1971.08,"prove_ram_MB":1741.50}
    ],
    "GMiMC": [
        {"height":1,"setup_runtime":12.26,"prove_runtime":0.59,"setup_ram_MB":276.73,"prove_ram_MB":192.90},
        {"height":2,"setup_runtime":15.19,"prove_runtime":0.9,"setup_ram_MB":412.82,"prove_ram_MB":266.66},
        {"height":3,"setup_runtime":27.82,"prove_runtime":1.58,"setup_ram_MB":619.14,"prove_ram_MB":408.16},
        {"height":4,"setup_runtime":49.63,"prove_runtime":2.86,"setup_ram_MB":940.38,"prove_ram_MB":471.62},
        {"height":5,"setup_runtime":112.01,"prove_runtime":5.22,"setup_ram_MB":1571.92,"prove_ram_MB":610.10},
        {"height":6,"setup_runtime":228.15,"prove_runtime":9.9,"setup_ram_MB":2828.15,"prove_ram_MB":851.75},
        {"height":7,"setup_runtime":511.6,"prove_runtime":19.46,"setup_ram_MB":5546.74,"prove_ram_MB":1647.11},
        {"height":8,"setup_runtime":3475.97,"prove_runtime":38.27,"setup_ram_MB":10504.96,"prove_ram_MB":2727.77}
    ],
    "Poseidon": [
        {"height":1,"setup_runtime":1.97,"prove_runtime":0.42,"setup_ram_MB":164.22,"prove_ram_MB":166.54},
        {"height":2,"setup_runtime":4.83,"prove_runtime":0.48,"setup_ram_MB":175.56,"prove_ram_MB":190.76},
        {"height":3,"setup_runtime":10.5,"prove_runtime":0.61,"setup_ram_MB":194.70,"prove_ram_MB":241.51},
        {"height":4,"setup_runtime":19.25,"prove_runtime":0.71,"setup_ram_MB":221.66,"prove_ram_MB":310.98},
        {"height":5,"setup_runtime":31.27,"prove_runtime":1,"setup_ram_MB":264.76,"prove_ram_MB":401.55},
        {"height":6,"setup_runtime":54.04,"prove_runtime":1.54,"setup_ram_MB":340.99,"prove_ram_MB":390.29},
        {"height":7,"setup_runtime":67.36,"prove_runtime":2.42,"setup_ram_MB":416.49,"prove_ram_MB":412.55},
        {"height":8,"setup_runtime":79.05,"prove_runtime":4.5,"setup_ram_MB":668.99,"prove_ram_MB":503.60}
    ],
    "Poseidon2": [
        {"height":1,"setup_runtime":1.86,"prove_runtime":0.43,"setup_ram_MB":163.34,"prove_ram_MB":166.37},
        {"height":2,"setup_runtime":4.3,"prove_runtime":0.48,"setup_ram_MB":175.36,"prove_ram_MB":192.04},
        {"height":3,"setup_runtime":9.23,"prove_runtime":0.56,"setup_ram_MB":197.91,"prove_ram_MB":241.44},
        {"height":4,"setup_runtime":17.5,"prove_runtime":0.73,"setup_ram_MB":224.00,"prove_ram_MB":306.30},
        {"height":5,"setup_runtime":27.15,"prove_runtime":1,"setup_ram_MB":262.95,"prove_ram_MB":378.71},
        {"height":6,"setup_runtime":41.07,"prove_runtime":1.66,"setup_ram_MB":334.49,"prove_ram_MB":394.08},
        {"height":7,"setup_runtime":57.48,"prove_runtime":2.57,"setup_ram_MB":429.20,"prove_ram_MB":396.07},
        {"height":8,"setup_runtime":71.47,"prove_runtime":4.45,"setup_ram_MB":727.54,"prove_ram_MB":451.05}
    ],
    "Neptune": [
        {"height":1,"setup_runtime":7.63,"prove_runtime":0.47,"setup_ram_MB":191.92,"prove_ram_MB":167.41},
        {"height":2,"setup_runtime":21.1,"prove_runtime":0.54,"setup_ram_MB":205.19,"prove_ram_MB":192.65},
        {"height":3,"setup_runtime":36.98,"prove_runtime":0.63,"setup_ram_MB":245.77,"prove_ram_MB":234.83},
        {"height":4,"setup_runtime":39.98,"prove_runtime":0.87,"setup_ram_MB":307.06,"prove_ram_MB":308.68},
        {"height":5,"setup_runtime":46.34,"prove_runtime":1.4,"setup_ram_MB":446.66,"prove_ram_MB":399.24},
        {"height":6,"setup_runtime":82.83,"prove_runtime":2.18,"setup_ram_MB":617.84,"prove_ram_MB":411.88},
        {"height":7,"setup_runtime":145.87,"prove_runtime":3.79,"setup_ram_MB":1022.12,"prove_ram_MB":471.51},
        {"height":8,"setup_runtime":283.62,"prove_runtime":6.79,"setup_ram_MB":1609.21,"prove_ram_MB":619.98}
    ]
}

base_dir = os.path.dirname(os.path.abspath(__file__))
output_data_path = os.path.join(base_dir, '../data/metrics_data.json')
with open(output_data_path, 'w') as f:
    json.dump(data, f, indent=2)