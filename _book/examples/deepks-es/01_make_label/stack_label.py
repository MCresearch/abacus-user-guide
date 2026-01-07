import os
import numpy as np
import glob
import re

# --- Parameter Configuration ---
# Specify the base names of the npy files to be processed.
# The script will construct the full filename, e.g., "deepks_descriptor.npy".
FILE_TYPES_TO_PROCESS = [
    "atom",
    "box",
    "energy",
    "force",
    "hamiltonian",
    "overlap"
]

# --- Main Script Logic ---
def main():
    """
    Main function to find, stack, and save npy files.
    """
    # Find all group.0* directories in the current path.
    group_dirs = sorted(glob.glob("group.0*"))
    if not group_dirs:
        print("Error: No 'group.0*' directories found in the current path.")
        return

    print(f"Found the following group directories: {group_dirs}")

    # Iterate over each group directory.
    for group_dir in group_dirs:
        abacus_path = os.path.join(group_dir, "ABACUS")
        if not os.path.isdir(abacus_path):
            print(f"Warning: 'ABACUS' directory not found in '{group_dir}', skipping.")
            continue
        
        print(f"\n--- Processing: {group_dir} ---")

        # Iterate over each type of file to be processed.
        for file_type in FILE_TYPES_TO_PROCESS:
            # Assemble the filename and search pattern.
            deepks_filename = f"deepks_{file_type}.npy"
            search_pattern = os.path.join(abacus_path, "*", "OUT.ABACUS", deepks_filename)
            
            # Find all matching files.
            npy_files = sorted(glob.glob(search_pattern))
            
            # Filter out paths that are not in a numeric directory.
            # This checks that the parent of "OUT.ABACUS" is a directory with a numeric name.
            npy_files = [f for f in npy_files if os.path.basename(os.path.dirname(os.path.dirname(f))).isdigit()]

            if not npy_files:
                print(f"'{deepks_filename}' not found in {group_dir}.")
                continue

            print(f"Found {len(npy_files)} '{deepks_filename}' files, preparing to stack...")

            # Read all found npy files into a list.
            data_list = [np.load(f) for f in npy_files]

            # stack along a new first axis.
            try:
                stackd_data = np.stack(data_list, axis=0)
            except ValueError as e:
                print(f"Error: Dimension mismatch when concatenating '{deepks_filename}': {e}")
                print("Please check if the dimensions of the following files are consistent:")
                for f in npy_files:
                    print(f"  - {f}  shape: {np.load(f).shape}")
                continue

            # Determine the output filename.
            output_filename = f"{file_type}.npy"
            output_path = os.path.join(group_dir, output_filename)

            # Save the stackd array.
            np.save(output_path, stackd_data)
            print(f"Successfully stackd and saved to: {output_path}")
            print(f"  - Number of input files: {len(data_list)}")
            print(f"  - Shape of input data: {data_list[0].shape}")
            print(f"  - Shape of output array: {stackd_data.shape}")


if __name__ == "__main__":
    main()