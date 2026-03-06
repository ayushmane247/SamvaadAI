from scheme_service.scheme_loader import load_schemes

schemes = load_schemes()

print("Schemes loaded:", len(schemes))

for s in schemes:
    print(s["scheme_id"])