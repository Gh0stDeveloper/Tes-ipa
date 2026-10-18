# S4NTOS INJECTOR — Hotfix de versión sobre el IPA ORIGINAL

Este flujo existe porque la reconstrucción experimental de la rama `feat/s4ntos-v2-source` utilizó **fuentes públicas 3105 versión 2.0**, mientras que la aplicación que el cliente probó satisfactoriamente provino del **IPA 2.1 Beta 2**. Poner una versión más alta a una compilación antigua no recupera funciones añadidas en el ejecutable 2.1.

## Qué cambia exactamente

- Fuente: `S4NTOS_INJECTOR_unsigned.ipa` del primer ZIP ya probado, basado en `2.1 Beta 2`.
- Recompila únicamente el catálogo del icono y splash utilizando los mismos recursos aprobados.
- Conserva el ejecutable **byte a byte**, salvo el reemplazo de la terminación `latest` por `nosync` en la URL del *updater* heredado (ambas cadenas tienen seis bytes). Evita que **el comprobador de actualización integrado** consulte releases ajenas al proyecto S4NTOS. Esto no afecta la firma de iOS, pero significa que **se desactiva la notificación de futuras actualizaciones automáticas del proyecto original**.
- Metadatos: `CFBundleDisplayName` y `CFBundleName` = `S4NTOS INJECTOR`, versión **2.2.1**, build **2201**, `AppReleaseDisplayVersion = 2.2.1 · S4NTOS INJECTOR`, bundle ID = `com.s4ntos.injector`.
- Incluye `S4NTOSBuildMarker = S4NTOS-ORIGINAL-2.1-BETA2-VERSION-HOTFIX-2201` para distinguirlo de una instalación anterior.

El flujo valida con una comparación binaria exacta que el ejecutable sea el del primer IPA, excepto esos seis bytes; no se transpila/reconstruye código Swift.

## Qué no cambia (importante)

- **Esta rama es el arreglo de versiones y de avisos heredados, no la solución de Home/New ni de los nombres de los créditos.** Esas vistas permanecen como en el IPA de primera pasada; requieren modificar el código fuente coincidente con 2.1 Beta 2 o un parche bien verificado sin perder funciones. No se deben fusionar inadvertidamente los cambios del proyecto 2.0 antiguo.
- Cualquier aviso que **GBox o ESign** muestre **antes de abrir la app** es propio de la firma, certificado, provisionamiento o instalador; cambiar `Info.plist` o la URL del updater interno no puede garantizar que esas herramientas oculten ese aviso.
- El IPA generado es **unsigned**; se requiere una firma válida para su instalación.

## CI y validaciones

Workflow: `.github/workflows/original-ipa-hotfix.yml`. Descarga el artefacto `S4NTOS-INJECTOR-2.2.1-ORIGINAL-IPA`, extrae el .ipa, fírmarlo en GBox/ESign usando tu certificado válido. En iPhone comprueba **2.2.1 · S4NTOS INJECTOR** y todas las funciones que operaban en la versión anterior.

## Licencias / procedencia

Los elementos de la aplicación original derivan del proyecto [YangJiiii/3105](https://github.com/YangJiiii/3105), bajo GPL-3.0 y con atribuciones de terceros. Conservar los créditos técnicos y el texto de licencia en la documentación distribucional y cumplir con las obligaciones de código fuente aplicables. Las redes sociales del cliente son distintas de la atribución de código original.

No fusionar a `main` antes de una prueba en un dispositivo físico.
