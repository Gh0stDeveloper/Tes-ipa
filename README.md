# S4NTOS INJECTOR — iOS IPA branding & signing

Pipeline de GitHub Actions para reconstruir el catálogo de recursos (icono y pantalla inicial) de una aplicación iOS **ya compilada** y, opcionalmente, firmar el resultado para instalación en dispositivos autorizados.

**Estado:** configurado para compilar en runners macOS; la instalación depende de una firma iOS válida. No compila el código Swift/Objective-C original porque solo se dispone de un IPA. La integridad del archivo no implica que la app vaya a ejecutarse correctamente.

## Archivo de entrada

Sube **`S4NTOS_INJECTOR_kit_para_GitHub.zip`** a la raíz de este repositorio. El ZIP, generado a partir de la imagen suministrada y el IPA del proyecto, debe contener:

- `S4NTOS_INJECTOR_unsigned.ipa` (variante modificada, sin firmar).
- `Assets.xcassets/` (icono **S4NTOS INJECTOR**, splash).
- Un README y scripts auxiliares incluidos en el paquete; **GitHub Actions no ejecuta scripts procedentes del ZIP**.

> **Privacidad:** este repositorio es público. Si el IPA no se puede distribuir, conviértelo en privado antes de subirlo. Alternativamente ejecuta Actions manualmente con una URL HTTPS temporal en el campo `kit_url` para que el ZIP no quede comprometido en el historial Git; el contenido sí se almacenará en los artefactos de la ejecución.

## Compilación

1. Abre **Actions → S4NTOS INJECTOR — iOS build/sign → Run workflow**, o sube el ZIP (un push a `main` lo dispara).
2. Sin credenciales, obtendrás el artefacto `S4NTOS-INJECTOR-unsigned`. **No es instalable directamente sin firmar**.
3. Con credenciales configuradas y compatibles, Actions también publica `S4NTOS-INJECTOR-signed`, un IPA firmado para el método de distribución de tu perfil.

El workflow compila `Assets.car` con Xcode, actualiza las referencias de icono y splash, reempaqueta el IPA, verifica el ejecutable y realiza `codesign` si hay firma.

## Instalación con GBox o ESign (sin cuenta Apple Developer)

La modalidad principal de este repositorio es **IPA sin firmar**, lista para importar a GBox o ESign y firmar **en el dispositivo**. El runner de GitHub no puede firmar por esas herramientas.

1. Abre [Actions](https://github.com/Gh0stDeveloper/Tes-ipa/actions/workflows/build-sign-ios.yml), entra a la última ejecución y confirma que **Compile catalog and optionally sign IPA** terminó en verde.
2. Descarga el artefacto **S4NTOS-INJECTOR-unsigned** y **descomprime el ZIP que entrega GitHub**: adentro está `S4NTOS_INJECTOR_compiled_unsigned.ipa`.
3. Importa ese archivo **.ipa** en GBox o ESign, y selecciona su función de firma. Necesitas un certificado/perfil **válido y compatible** con la distribución a tu dispositivo; usar esas aplicaciones no equivale a disponer de una firma aceptada por iOS.
4. Firma e instala; sigue solo las instrucciones de confianza/administración de dispositivos de iOS correspondientes a **tu** certificado. Si iOS rechaza la firma, está revocada o no incluye tu dispositivo, necesitarás otra firma válida.
5. Comprueba en el iPhone: nombre, icono, splash y que la aplicación arranque y conserve sus funciones.

**Bundle identifier:** la compilación cambia el identificador reservado `com.apple.mobile.MobileHouseArrest` por `com.s4ntos.injector`. En la ejecución manual del workflow puedes modificar el campo `bundle_id`. Como el ejecutable original incluye referencias al identificador anterior, **no se garantiza que todas sus funciones operen después del cambio**. Un IPA compilado o firmado no es lo mismo que una app probada en un iPhone.

**Privacidad y seguridad:** utiliza certificados y herramientas de firma de procedencia confiable. No compartas tu Apple ID, contraseñas, certificados privados o perfiles en el repositorio ni los introduzcas en servicios que no sean de tu confianza.

## Configuración de firma

En **Settings → Secrets and variables → Actions → New repository secret**, crea los siguientes secretos:

| Nombre | Descripción |
|---|---|
| `IOS_P12_BASE64` | Certificado de firma Apple + clave privada, exportado como archivo .p12 y codificado en Base64 (una línea). |
| `IOS_P12_PASSWORD` | Contraseña del archivo .p12. |
| `IOS_PROFILE_BASE64` | Perfil .mobileprovision codificado en Base64 (una línea). |
| `IOS_BUNDLE_ID` | **Opcional:** identificador de aplicación autorizado por el perfil. Obligatorio si el App ID del perfil termina en `.*`. |

El **perfil y certificado deben corresponder a un mismo equipo de desarrollo**. El perfil debe permitir instalar en el dispositivo; con **Ad Hoc** o desarrollo, los UDID de los iPhone deben estar incluidos. Un certificado de distribución App Store no convierte un IPA en instalable por sideloading.

El IPA original indica el identificador reservado `com.apple.mobile.MobileHouseArrest`. La compilación lo sustituye por `com.s4ntos.injector` (configurable); la fase opcional de firma puede cambiarlo de nuevo al ID autorizado por el perfil, sin modificar el ejecutable. Si la app depende de ese ID a nivel interno, puede no funcionar. No se sortean controles de seguridad ni activación.

**No subas claves privadas, contraseñas ni .mobileprovision al repositorio.**

## Instalación

Descarga el IPA del artefacto firmado en la página de Actions. Instálalo únicamente mediante el método autorizado por tu perfil (Apple Configurator, MDM, distribución Ad Hoc o mecanismo equivalente). Algunas apps pueden requerir servicios/entitlements no disponibles para cuentas personales o permisos del proveedor original.

Si todavía no tienes certificado, el artefacto unsigned compilado puede re-firmarse con una herramienta legítima como Sideloadly/AltStore con tu propia cuenta; el re-firmado y la instalación son pasos independientes de esta acción.

## Límites y comprobaciones

- Requiere iOS 16+ y arquitectura arm64.
- Icono y splash se compilan con `xcrun actool` en macOS.
- El workflow **no verifica el uso real en un iPhone** y no garantiza compatibilidad con la firma.
- La cadena `Developer by S4NTOS INJECTOR` se modifica en recursos localizados; sin código fuente no puede garantizarse que no exista otra cadena incrustada directamente en el binario.

Archivos de automatización: `.github/workflows/build-sign-ios.yml`, `scripts/compile_ipa.sh` y `scripts/sign_ipa.sh`.
