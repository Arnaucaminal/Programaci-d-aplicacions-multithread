import gzip
import os
import shutil
import sys
import time
from pathlib import Path

if __name__ == "__main__":

    # Demanem els paths d'origen i de destí a l'usuari.
    dir_origen = input("Path de la carpeta origen: ")
    path_origen = Path(dir_origen)
    dir_desti = input("Path de la carpeta de destí: ")
    path_desti = Path(dir_desti)

    # Comprovem si el path d'origen no existeix o no és un directori.
    if not path_origen.exists() or not path_origen.is_dir():
        print("El path d'origen no existeix o no és un directori.", file=sys.stderr)
        exit(101)

    # Comprovem si ens falta algun dels permisos mínims sobre el directori d'origen.
    if not os.access(path_origen, os.R_OK | os.X_OK):
        print("El path d'origen no té els permisos mínims.", file=sys.stderr)
        exit(102)

    # Comprovem si el path de destí existeix, o no.
    if not path_desti.exists():
        # Si no existeix, creem el directori.
        path_desti.mkdir(parents=True)
    else:
        # Si existeix, comprovem que sigui un directori.
        if not path_desti.is_dir():
            print("El path de destí existeix però no és un directori.", file=sys.stderr)
            exit(103)

        # Comprovem, també, si ens falta algun dels permisos mínim.
        if not os.access(path_desti, os.W_OK | os.X_OK):
            print("El path de destí no té els permisos mínims.", file=sys.stderr)
            exit(104)

    errors = False
    dirs = ""

    # Iniciem el comptatge de temps d'execució.
    inici = time.perf_counter_ns()

    # Executem la funció equivalent a la comanda ls o dir sobre el directori origen.
    for elem in path_origen.glob("*"):
        print(elem)

        # Comprovem si l'element actual és un arxiu, o no.
        if elem.is_file():
            # Si l'element actual és un arxiu, el copiem al directori de destí
            # comprimint-lo en format gzip.
            try:
                with open(elem, 'rb') as arxiu_origen:
                    with gzip.open(path_desti / (elem.name + ".gz"), 'wb') as arxiu_desti:
                        shutil.copyfileobj(arxiu_origen, arxiu_desti)
            except PermissionError as pe:
                print("Error de permisos: %s" % pe)
                errors = True
            except IOError as e:
                print("Error d'E/S comprimint %s: %s" % (elem.name, e), file=sys.stderr)
                errors = True

        elif elem.is_dir():
            # Si l'element actual és un directori, guardem el seu nom en un
            # string que anirà acumulant tots els noms de subdirectoris.
            dirs += elem.name + "\n"

    # Si hi havia subdirectoris escrivim l'arxiu amb els noms.
    if dirs != "":
        try:
            with open(path_desti / "directoris.txt", "wt") as arxiu_dirs:
                arxiu_dirs.write(dirs)
        except IOError as e:
            print("Error escrivint llista de directoris: %s" % e, file=sys.stderr)
            errors = True

    # Finalitzem el comptatge de temps i el mostrem a l'usuari.
    final = time.perf_counter_ns()
    temps = (final - inici) / 1000000000.0
    print("Temps: %.2f seg." % temps)

    # Donem missatge de finalització i, si hi ha hagut algun error durant el procés,
    # informem a l'usuari.
    print("Procés finalitzat.")
    if errors:
        print("S'han registrat errors. Reviseu els resultats.", file=sys.stderr)