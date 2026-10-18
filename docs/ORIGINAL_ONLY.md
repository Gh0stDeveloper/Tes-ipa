# S4NTOS INJECTOR — Personalización EXCLUSIVAMENTE del IPA original

**Fuente única:** `SantosXit🍎_vsAlta.ipa` → ejecutable SHA-256 `d5b95ed6ce634cb5f8f8734f31e4a83212a3341ad59389706482a796cdfbab7b`. El primer kit `S4NTOS_INJECTOR_kit_para_GitHub.zip` contiene ese mismo ejecutable y los iconos/splash ya aprobados.

**Este flujo no clona ni consulta código fuente de terceros para compilar.** Ejecuta `scripts/patch_original_only.py` sobre ese ejecutable exacto, recompila únicamente las imágenes previamente aprobadas mediante `xcrun actool` y empaqueta el IPA sin firmar para GBox o ESign.

## Cambios solicitados en la marca del cliente

- Nombre: `S4NTOS INJECTOR`.
- Icono y splash: recursos del primer ZIP, sin alteraciones de diseño.
- **About:** los títulos visibles de las filas de crédito de la app pasan a nombres de plataformas **TikTok, WhatsApp, Discord y Telegram**. Roles y enlaces se actualizan con @s4ntosxiter1, +573505589046, discord.gg/b6xnTpUK5w y @s4ntosOWNER.
- El diseño y el número de filas siguen siendo los originales. Algunas plataformas aparecerán en más de una fila porque **no se elimina ni recompila la vista original**. La URL de Telegram de una fila es `http://t.me/S4ntosOWNER` y redirige al enlace HTTPS; las otras filas usan HTTPS. Los sufijos de fragmento `#x` no cambian el destino web.

## NO se modifica

- Ejecutable funcional: solamente bytes específicos de *constantes de texto* e inmediatos Swift de etiquetas About. El SHA-256 del ejecutable de entrada se comprueba antes de editar.
- Versión: **2.1 Beta 2** (`CFBundleShortVersionString=2.1`, `CFBundleVersion=2`, `AppReleaseDisplayVersion=2.1 Beta 2`).
- Bundle ID: `com.apple.mobile.MobileHouseArrest`.
- Updater del proyecto original, catálogo de repositorios, capacidades de iOS y funciones avanzadas: **sin cambios**.
- Home y New: **sin cambios**, de acuerdo con el alcance acotado a icono, splash y contactos de este último pedido.

## Límites y validación

Los cambios de código de máquina se restringen a posiciones conocidas del binario original; no se aplican a ejecutables diferentes. GitHub Actions comprueba la identidad del IPA y su integridad después de compilar los recursos. **No es prueba de funcionamiento real**; hace falta instalar con una firma válida y probar contactos y funciones en el mismo dispositivo usado con el IPA original.

No se garantiza eliminar avisos del propio instalador GBox/ESign, ni se altera el sistema de actualización de 3105. Si la aplicación muestra una nueva versión disponible, es comportamiento original conservado.

## Atribución

Los enlaces de contacto del cliente son distintos de las atribuciones de autoría del software. La aplicación original deriva de [YangJiiii/3105](https://github.com/YangJiiii/3105) y utiliza otros trabajos. Al redistribuir la variante, deben preservarse los avisos y obligaciones de licencia aplicables (GPL-3.0 y contribuciones de terceros); ver [licencia](https://github.com/YangJiiii/3105/blob/main/LICENSE) y [avisos de terceros](https://github.com/YangJiiii/3105/blob/main/THIRD_PARTY_NOTICES.md).

**No fusionar a `main` hasta obtener la validación del cliente en un iPhone real.**
