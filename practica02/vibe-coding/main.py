import re

def validar_contrasena(password: str) -> tuple[bool, list[str]]:
    """
    Valida si una contraseña cumple con los criterios básicos de seguridad:
    - No estar vacía
    - Mínimo 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    errores = []

    if not password:
        return False, ["La contraseña no puede estar vacía."]

    if len(password) < 8:
        errores.append("Debe tener al menos 8 caracteres.")

    if not any(c.isupper() for c in password):
        errores.append("Debe contener al menos una letra mayúscula.")

    if not any(c.islower() for c in password):
        errores.append("Debe contener al menos una letra minúscula.")

    if not any(c.isdigit() for c in password):
        errores.append("Debe contener al menos un número.")

    caracteres_especiales = r"[!@#$%^&*(),.?\":{}|<>]"
    if not re.search(caracteres_especiales, password):
        errores.append("Debe contener al menos un carácter especial (!@#$%^&*...).")

    es_valida = len(errores) == 0
    return es_valida, errores


def probar_contrasena(password: str) -> None:
    valida, errores = validar_contrasena(password)
    estado = "VÁLIDA" if valida else "INVÁLIDA"
    print(f"Contraseña: '{password}' -> {estado}")
    if errores:
        for error in errores:
            print(f"  - {error}")


def validar_email(email: str) -> tuple[bool, list[str]]:
    """
    Valida si un correo electrónico tiene un formato válido:
    - No estar vacío
    - Contener estructura de usuario@dominio.extension
    """
    errores = []

    if not email:
        return False, ["El email no puede estar vacío."]

    patron_email = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"
    if not re.match(patron_email, email):
        errores.append("El formato del email no es válido (ejemplo esperado: usuario@dominio.com).")

    es_valido = len(errores) == 0
    return es_valido, errores


def probar_email(email: str) -> None:
    valido, errores = validar_email(email)
    estado = "VÁLIDO" if valido else "INVÁLIDO"
    print(f"Email: '{email}' -> {estado}")
    if errores:
        for error in errores:
            print(f"  - {error}")


def registrar_usuario(
    email: str, 
    password: str, 
    lista_usuarios: list[dict], 
    es_admin: bool = False
) -> tuple[bool, list[str]]:
    """
    Valida email y contraseña antes de agregar un nuevo usuario a la lista.
    Si es_admin=True, la validación de contraseña es opcional.
    Estructura de usuario: {"email": str, "password": str, "es_admin": bool}
    """
    errores = []

    # Validar email (siempre obligatorio)
    email_valido, errores_email = validar_email(email)
    if not email_valido:
        errores.extend(errores_email)

    # Verificar si el email ya existe en la lista
    if any(u["email"].lower() == email.lower() for u in lista_usuarios):
        errores.append("El email ya se encuentra registrado.")

    # Validar contraseña solo si NO es administrador
    if not es_admin:
        pass_valida, errores_pass = validar_contrasena(password)
        if not pass_valida:
            errores.extend(errores_pass)
    else:
        # Para administradores, la validación estricta es opcional (se acepta cualquier clave o vacía)
        pass

    if errores:
        return False, errores

    nuevo_usuario = {
        "email": email, 
        "password": password, 
        "es_admin": es_admin
    }
    lista_usuarios.append(nuevo_usuario)
    return True, []


def listar_usuarios(lista_usuarios: list[dict]) -> None:
    """Muestra la lista de usuarios registrados."""
    print(f"\n--- Lista de Usuarios Registrados ({len(lista_usuarios)}) ---")
    if not lista_usuarios:
        print("No hay usuarios registrados aún.")
        return

    for idx, u in enumerate(lista_usuarios, start=1):
        rol = "[ADMIN]" if u.get("es_admin") else "[USUARIO]"
        password_oculta = "*" * len(u["password"]) if u["password"] else "(sin contraseña)"
        print(f"{idx}. {rol} Email: {u['email']} | Contraseña: {password_oculta} ({u['password']})")


def main():
    print("=== Sistema de Registro y Validación de Usuarios ===")
    
    # Lista en memoria para almacenar los usuarios
    usuarios: list[dict] = []

    print("\n--- Pruebas de Registro ---")
    
    # Usuario normal (Válido)
    ok, errs = registrar_usuario("ana@correo.com", "AnaClave2026!", usuarios, es_admin=False)
    print(f"Registro Usuario normal 'ana@correo.com': {'EXITOSO' if ok else 'FALLIDO'}")
    if errs:
        for e in errs:
            print(f"  - {e}")

    # Usuario normal con clave débil (Falla)
    ok, errs = registrar_usuario("pedro@correo.com", "123", usuarios, es_admin=False)
    print(f"Registro Usuario normal 'pedro@correo.com' (clave '123'): {'EXITOSO' if ok else 'FALLIDO'}")
    if errs:
        for e in errs:
            print(f"  - {e}")

    # Administrador con clave débil (PASA sin validar contraseña)
    ok, errs = registrar_usuario("admin@sistema.com", "123", usuarios, es_admin=True)
    print(f"Registro Administrador 'admin@sistema.com' (clave '123'): {'EXITOSO' if ok else 'FALLIDO'}")
    if errs:
        for e in errs:
            print(f"  - {e}")

    # Administrador sin contraseña (PASA sin validar)
    ok, errs = registrar_usuario("superadmin@sistema.com", "", usuarios, es_admin=True)
    print(f"Registro Administrador 'superadmin@sistema.com' (sin clave): {'EXITOSO' if ok else 'FALLIDO'}")
    if errs:
        for e in errs:
            print(f"  - {e}")

    # Listar los usuarios registrados
    listar_usuarios(usuarios)

    # Registro interactivo
    print("\n--- Registro Interactivo ---")
    try:
        email_in = input("Ingresa tu email: ")
        pass_in = input("Ingresa tu contraseña: ")
        es_admin_in = input("¿Es administrador? (s/n): ").strip().lower() == "s"
        
        ok, errs = registrar_usuario(email_in, pass_in, usuarios, es_admin=es_admin_in)
        if ok:
            print("¡Usuario registrado exitosamente!")
        else:
            print("No se pudo registrar el usuario:")
            for e in errs:
                print(f"  - {e}")

        listar_usuarios(usuarios)
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo...")


if __name__ == "__main__":
    main()
