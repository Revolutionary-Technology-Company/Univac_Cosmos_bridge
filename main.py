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
import numpy as np

def calculate_pixel_to_physical_scale(f_objective, f_eyepiece, sensor_pixel_size_microns, object_distance_meters):
    """
    Calculates the true real-world size represented by a single camera pixel,
    accounting for telescopic magnification optics.
    """
    # 1. Compute optical magnification
    m_optical = f_objective / f_eyepiece
    
    # 2. Calculate the system's effective field of view scale factor
    # True feature size on sensor = Real size * (f_effective / Distance)
    effective_focal_length = f_objective * m_optical
    
    # 3. Size of one pixel in meters (e.g., 1.4 microns = 1.4e-6)
    pixel_size_meters = sensor_pixel_size_microns * 1e-6
    
    # 4. Map one pixel to real world physical distance (meters per pixel)
    meters_per_pixel = (pixel_size_meters * object_distance_meters) / effective_focal_length
    
    return meters_per_pixel

def infer_molecular_density(meters_per_pixel, structural_bounding_box_pixels, lattice_constant_angstrom):
    """
    Bridges the macro image from a Tesla/Mobile camera down to the atomic scale.
    Calculates how many atomic unit cells span the captured object.
    """
    # Convert pixels to actual physical size of the scanned part (e.g., a wing strut)
    total_physical_width_meters = structural_bounding_box_pixels * meters_per_pixel
    
    # Convert Angstroms to meters (1 Angstrom = 1e-10 meters)
    lattice_constant_meters = lattice_constant_angstrom * 1e-10
    
    # Calculate total atomic repetitions required for your Cosmos CAD engine
    required_lattice_repetitions = total_physical_width_meters / lattice_constant_meters
    
    return int(required_lattice_repetitions)

# --- SYSTEM INTEGRATION EXAMPLE FOR YOUR MAINFRAME ---
# Scenario: A Tesla camera (f_obj=4.5mm) with a telescopic mod detects a component 5 meters away
meters_per_px = calculate_pixel_to_physical_scale(
    f_objective=45.0,        # 45mm telephoto/telescopic attachment
    f_eyepiece=4.5,          # 4.5mm base receiver lens
    sensor_pixel_size_microns=1.4, 
    object_distance_meters=5.0
)

# If Univac-IX identifies the material as Titanium (Lattice Constant = 3.30 Angstroms)
# and the object is 800 pixels wide in the camera feed:
total_atoms_wide = infer_molecular_density(
    meters_per_pixel=meters_per_px,
    structural_bounding_box_pixels=800,
    lattice_constant_angstrom=3.30
)

print(f"Mainframe Telemetry: Scale is {meters_per_px:.4e} meters per pixel.")
print(f"Procedural Target: Generate a CAD model lattice with {total_atoms_wide} molecular repetitions.")

