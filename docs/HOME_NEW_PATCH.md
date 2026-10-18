# S4NTOS INJECTOR — Home y New sin resultados (IPA original)

Este cambio parte **solo** de la aplicación del cliente `SantosXit🍎_vsAlta.ipa`, edición original **2.1 Beta 2**, con el parche anterior de contactos, icono y splash. No descarga ni compila el código de ninguna otra versión.

## Cambios

- **Home**: la función propia `PackageRepositoryFeedPolicy.home` devuelve un arreglo Swift vacío.
- **New**: la función propia `PackageRepositoryFeedPolicy.newest` devuelve un arreglo Swift vacío.
- **Sources / Installed / Files**: los datos y operaciones permanecen intactos; no se borran fuentes, paquetes o configuraciones.
- **About**: conservados los contactos de S4NTOS del parche anterior.
- **Icono y splash**: el catálogo de imágenes aprobado anteriormente se recompila con Xcode.

El parche ARM64 revisa primero el SHA-256 exacto del ejecutable 2.1 Beta 2 ya personalizado y los prólogos de las dos funciones. Solo sustituye 8 instrucciones en cada función, liberando el arreglo de entrada y devolviendo la instancia compartida vacía de Swift. Si cambia la versión binaria, el parche falla en vez de modificar offsets sin verificar.

## Qué sigue intacto

- `CFBundleShortVersionString=2.1`, `CFBundleVersion=2`, `AppReleaseDisplayVersion=2.1 Beta 2`.
- Bundle ID `com.apple.mobile.MobileHouseArrest`.
- Comprobador de actualizaciones original y URLs del catálogo.
- Motores de compatibilidad iOS, permisos y restantes funciones.

## Límites visuales y pruebas

**Se eliminan los paquetes/anuncios del feed de Home y New.** Al quedar las listas vacías, **la interfaz original todavía puede mostrar su pantalla «No packages» o «No sources»**: este parche no recompila los cuerpos de SwiftUI ni elimina las tarjetas de estado vacío. No debe describirse como una pantalla 100% en blanco antes de una validación visual en un iPhone.

El IPA es **unsigned** y necesita ser firmado con un certificado válido mediante GBox/ESign. No se garantiza la instalación ni funcionalidad con todas las versiones iOS hasta probarlo en dispositivo.

Se conservan las obligaciones de atribución/licencia del código original: [3105 GPL](https://github.com/YangJiiii/3105/blob/main/LICENSE) y [avisos a colaboradores](https://github.com/YangJiiii/3105/blob/main/THIRD_PARTY_NOTICES.md).

No fusionar a `main` hasta la prueba manual.
