import os, sys

#   \/:*?"<>|


def recherche(pattern, rep=os.curdir, depth=-1, inverse=False, verbose=False):
    """
    Spécifications:
        Permet de rechercher un fichier de façon récursive
        depuis le fichier précisé.
        les patterns prennent en compte :
            * <=> tout caractère, autant de fois que possible
            ? <=> tout caractère, une fois
            ! <=> tout caractère, zéro ou une fois

    paramètres:
        pattern: chaîne de caractère; pattern des fichiers à rechercher
        rep: chaîne de caractère; dossier racine de la recherche
        depth: nombre de sous-répertoire à rechercher avant de s'arrêter (defaut: -1)
            mettre -1 pour une recherche sans limite
        inverse: booléen; affiche seulement les fichiers qui ne correspondent pas au pattern
        verbose: booléen; afficher les erreurs dans le flux sys.stderr (2)
    """
    #print(f"pattern: {pattern}, rep={rep}, depth={depth}, inverse={inverse}, verbose={verbose}")
    if depth == 0: return
    if os.path.isdir(rep):
        rep_scan = os.scandir(rep)
        for file in rep_scan:
            if file.is_dir():
                try:
                    recherche(pattern, file.path, depth-1, inverse, verbose)
                except PermissionError:
                    if verbose: print(f"Permission denied: {file.path}.", file=sys.stderr)
                except RecursionError:
                    if verbose: print("Recursion Error: Depth limit reached.", file=sys.stderr)
                except Exception:
                    if verbose: print("Error Unknown.", file=sys.stderr)

            elif file.is_file():
                if _match(file.name, pattern) != inverse:
                    print(file.path)


def _match(name, pattern) -> bool:

    """
    les patterns prennent en compte :
        * <=> tout caractère, autant de fois que possible
        ? <=> tout caractère, une fois
        ! <=> tout caractère, zéro ou une fois
        caractère <nb> <=> répétition entre 0 et nb du caractère
        caractère <min:max> <=> répétition entre min et max du caractère
    """

    t = len(name)
    u = len(pattern)

    #print((name, pattern))

    if (t, u) == (0, 0):
        return True
    if u == 0:
        return False

    if u > 1 and pattern[1] == "<":
        if 0 < pattern.find(":") < pattern.find(">"):
            # Cas <min:max>
            return _verify(_create_iteration(_match,
                        lambda params: (params[0], pattern[0] + params[1]),
                        int(pattern[2:pattern.find(":")]),
                        int(pattern[pattern.find(":")+1:pattern.find(">")]),
                        name, pattern[pattern.find(">")+1:]))
        # Cas <nb>
        return _verify(_create_iteration(_match,
                        lambda params: (params[0], pattern[0] + params[1]),
                        0,
                        int(pattern[2:pattern.find(">")]),
                        name, pattern[pattern.find(">")+1:]))
    
    if pattern[0] == "*":
        return (_match(name, pattern[1:])
            or ( t and  _match(name[1:], pattern) )
            or _match(name[1:], pattern[1:]))
    
    if pattern[0] == "!":
        return ((t, u) == (1, 1)
            or _match(name, pattern[1:])
            or _match(name[1:], pattern[1:]))

    if t: # Mettre ici les fonctions qui obligent un caractère
        if (pattern[0] == "?") or (name[0] == pattern[0]):
            return _match(name[1:], pattern[1:])

    return False


def _verify(functions: tuple) -> bool:
    for function in functions:
        if function():
            return True
    return False

def _create_iteration(function, modification, min, max, *params) -> tuple:
    it = []
    for _ in range(min): params = modification(params)
    for _ in range(max-min +1):
        it.append(lambda params=params: function(*params))
        params = modification(params)
    return tuple(it)

#  _create_iteration(_match, lambda params: (params[0], params[1][0] + params[1]), n, name, pattern[0] + pattern[4:])
#   si params == (name, "haha"), nb_iter = 3 -> (_match(name, "haha"), _match(name, "hhaha"), _match(name,  "hhhaha"))

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc == 1 or argc > 6:
        print("Usage: (Pattern) [Location] [Depth] [Inverse] [Verbose]")
    else:
        recherche(*sys.argv[1:])