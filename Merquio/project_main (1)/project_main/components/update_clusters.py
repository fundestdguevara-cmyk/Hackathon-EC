import subprocess
import os

print("🔄 Actualizando clusters...")

# Eliminar datos pre-computados antiguos
if os.path.exists('precomputed_data'):
    import shutil
    shutil.rmtree('precomputed_data')
    print("🗑️  Datos antiguos eliminados")

# Ejecutar pre-cálculo
exec(open('precompute_clusters.py').read())

print("✅ Clusters actualizados exitosamente")