# univac_cell_map.py
"""
Authoritative Structural Reference Map linking incoming multi-spectrum data strings
to internal cross-page calculation sheets inside the Univac-IX repository.
"""

UNIVAC_EXCEL_CELL_MAP = {
    # -------------------------------------------------------------------------
    # INPUT INGESTION MAP: Where the mainframe writes raw incoming network data.
    # -------------------------------------------------------------------------
    "INPUT_MAPPINGS": {
        "permittivity": {
            "sheet_name": "Sensor_Ingestion",
            "cell": "A2",
            "description": "Raw dielectric constant calculated from antenna phase shifts."
        },
        "conductivity": {
            "sheet_name": "Sensor_Ingestion",
            "cell": "B2",
            "description": "Bulk ionic conductivity measured in Siemens per meter (S/m)."
        },
        "scan_frequency": {
            "sheet_name": "Sensor_Ingestion",
            "cell": "C2",
            "description": "Active operational frequency band (e.g., 24.12e9 for Radar)."
        }
    },

    # -------------------------------------------------------------------------
    # OUTPUT EXTRACTION MAP: Where the engine scrapes final calculated properties.
    # -------------------------------------------------------------------------
    "OUTPUT_MAPPINGS": {
        "material_classification": {
            "sheet_name": "Material_Outputs",
            "cell": "C2",
            "description": "Inferred physical composition state resolved by the state machine."
        },
        "mass_density": {
            "sheet_name": "Material_Outputs",
            "cell": "D2",
            "description": "Calculated structural material density in grams per cubic centimeter (g/cm³)."
        },
        "yield_strength": {
            "sheet_name": "Material_Outputs",
            "cell": "E2",
            "description": "Tensile stress failure threshold computed via aviation load formulas."
        },
        "lattice_type": {
            "sheet_name": "Lattice_Analytics",
            "cell": "B2",
            "description": "Atomic crystal structural configuration array profile (e.g., FCC, BCC, HCP)."
        },
        "lattice_spacing": {
            "sheet_name": "Lattice_Analytics",
            "cell": "C2",
            "description": "Microscopic lattice plane constant value extracted in Angstrom units (Å)."
        },
        "packing_factor": {
            "sheet_name": "Lattice_Analytics",
            "cell": "D2",
            "description": "Calculated atomic packing volume efficiency fraction (dimensionless ratio)."
        }
    }
}

class ExcelCellOrchestrator:
    def __init__(self, workbook_instance):
        self.wb = workbook_instance
        self.mappings = UNIVAC_EXCEL_CELL_MAP

    def inject_inputs(self, network_payload_dict):
        """Iterates through input mappings and populates raw data points into the ledger cells."""
        input_rules = self.mappings["INPUT_MAPPINGS"]
        
        for variable_key, mapping_rules in input_rules.items():
            if variable_key in network_payload_dict:
                sheet = self.wb[mapping_rules["sheet_name"]]
                target_cell = mapping_rules["cell"]
                
                # Assign the raw data into the live cell position
                sheet[target_cell] = network_payload_dict[variable_key]
                print(f"-> Injected input [{variable_key}] -> {mapping_rules['sheet_name']}!{target_cell}")

    def extract_calculated_json(self):
        """Scrapes values from the calculated sheets after the internal matrix formulas resolve."""
        output_rules = self.mappings["OUTPUT_MAPPINGS"]
        extracted_data = {
            "telemetry_inversion": {},
            "material_profile": {},
            "molecular_lattice": {}
        }
        
        # Populate the extraction tree dynamically by executing the mapped grid coordinates
        m_out = output_rules["material_classification"]
        d_out = output_rules["mass_density"]
        y_out = output_rules["yield_strength"]
        
        extracted_data["material_profile"] = {
            "state": self.wb[m_out["sheet_name"]][m_out["cell"]].value,
            "density": self.wb[d_out["sheet_name"]][d_out["cell"]].value,
            "yield_strength_mpa": self.wb[y_out["sheet_name"]][y_out["cell"]].value
        }
        
        l_out = output_rules["lattice_type"]
        s_out = output_rules["lattice_spacing"]
        p_out = output_rules["packing_factor"]
        
        extracted_data["molecular_lattice"] = {
            "type": self.wb[l_out["sheet_name"]][l_out["cell"]].value,
            "spacing_angstrom": self.wb[s_out["sheet_name"]][s_out["cell"]].value,
            "packing_factor": self.wb[p_out["sheet_name"]][p_out["cell"]].value
        }
        
        return extracted_data
