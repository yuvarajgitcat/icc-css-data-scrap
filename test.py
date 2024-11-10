def print_sitrep_parts(sitrep):
    # Split the Sitrep text by commas
    parts = sitrep.split(',')
    
    # Print each part individually
    print("Parts extracted from the Sitrep:")
    for i, part in enumerate(parts, 1):
        print(len(parts))
        print(f"Part {i}: {part.strip()}")

# Test with a sample sitrep
sitrep = "24.11.2022: 1450 UTC: Posn: 10:16N – 064:34W, Guanta Anchorage."

print_sitrep_parts(sitrep)
