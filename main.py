import sys
import pandas as pd
import numpy as np
import trimesh

# Force Python to look inside your sibling repositories for modules
sys.path.append('../Univac-IX')
sys.path.append('../Basic-Aviation-Knowledge')
sys.path.append('../cosmos')

# 1. Import tools from your repositories
# (Adjust these import names to match the exact filename/class in your repos)
try:
    from univac_core import VisualDetector  
    from aviation_physics import StructuralStressTest  
except ImportError:
    print("Running in simulation mode. Connect your real repository modules.")

def load_lattice_db(excel_path):
    """Parses your Univac-IX Excel spreadsheet."""
    return pd.read_excel(excel_path)

def generate_molecular_cad(material_name, lattice_type, spacing, repetitions=10):
    """Procedurally generates the molecular CAD structure."""
    print(f"Generating {lattice_type} lattice for {material_name}...")
    atoms = []
    
    # Set coordinates based on the crystal structure type
    if lattice_type == 'BCC':
        unit_points = [[0,0,0], [0.5, 0.5, 0.5]] 
    elif lattice_type == 'FCC':
        unit_points = [[0,0,0], [0.5, 0.5, 0], [0.5, 0, 0.5], [0, 0.5, 0.5]]
    else: 
        unit_points = [[0,0,0]] # Default Simple Cubic

    # Build the structural 3D lattice
    for x in range(repetitions):
        for y in range(repetitions):
            for z in range(repetitions):
                base_pos = np.array([x, y, z]) * spacing
                for pt in unit_points:
                    atom_pos = base_pos + (np.array(pt) * spacing)
                    t_matrix = np.eye(4)
                    t_matrix[:3, 3] = atom_pos
                    
                    sphere = trimesh.creation.icosphere(radius=spacing*0.2)
                    sphere.apply_transform(t_matrix)
                    atoms.append(sphere)

    # Concatenate all individual atoms into one unified CAD mesh
    full_lattice = trimesh.util.concatenate(atoms)
    
    # Save the output file directly to your disk
    output_filename = f"{material_name}_lattice.stl"
    full_lattice.export(output_filename)
    print(f"Success! Saved CAD file: {output_filename}")
    return full_lattice

def run_pipeline(image_path, excel_path):
    """Executes the entire cross-repo workflow."""
    # Step A: Scan via Univac-IX
    # material = VisualDetector.scan(image_path)
    material = "Titanium_Alloy"  # Mock data for testing
    
    # Step B: Read properties from your Excel database
    df = load_lattice_db(excel_path)
    row = df[df['Material'] == material].iloc[0]
    
    # Step C: Procedurally generate molecular layout
    cad_mesh = generate_molecular_cad(material, row['LatticeType'], row['SpacingAngstrom'])
    
    # Step D: Test with Basic-Aviation-Knowledge physics
    print("Passing CAD data to planetary physics engine...")
    # StructuralStressTest.simulate_load(cad_mesh)

if __name__ == "__main__":
    # Point this to your actual Univac Excel file to test it!
    excel_file_location = "../Univac-IX/materials_db.xlsx" 
    print("Starting Material Engine Pipeline...")
    # run_pipeline("sample_object.jpg", excel_file_location)
