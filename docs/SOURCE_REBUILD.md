# S4NTOS INJECTOR — Segunda pasada (código fuente)

Esta rama prepara una **recompilación experimental desde SwiftUI** para corregir las dos limitaciones del parche del IPA: los nombres originales que continúan en la pantalla About y los resultados que reaparecen en Home y New desde fuentes locales/cache.

## Objetivo preciso

- **About / Contacto:** cuatro enlaces funcionales con nombre, identificador y URL correctos: TikTok (`@s4ntosxiter1`), WhatsApp (`+57 350 558 9046`), Discord (`https://discord.gg/b6xnTpUK5w`) y Telegram (`https://t.me/S4ntosOWNER`).
- **Home y New:** mostrar la pantalla vacía, sin tarjetas, resultados, avisos de ausencia ni indicadores de carga, aunque haya paquetes almacenados. Se conserva la barra inferior, el título y el botón de ajustes.
- **Marca:** nombre visible `S4NTOS INJECTOR`, icono y launch/splash previamente aprobados.
- **Sin alterar código funcional de exploración, parches, carpetas, permisos ni exploits**. El cambio de Bundle ID reproduce el de la versión de marca ya instalada, pero las funciones dependientes de MobileHouseArrest pueden variar.

## Construcción

El workflow `source-rebuild.yml` toma la revisión fija del proyecto de código abierto [YangJiiii/3105](https://github.com/YangJiiii/3105) (`a72617ed4c764a65d8aac1e91aca95231e72a2cb`), aplica `scripts/build_from_upstream.py`, compila en un runner macOS con Xcode y produce `S4NTOS_INJECTOR_source_unsigned.ipa` para firma posterior con GBox/ESign.

No se actualiza ni se elimina la compilación del IPA anterior. Este método recompila el programa desde la revisión 2.0 del proyecto original y **no garantiza paridad binaria o funcional** con el IPA 2.1 Beta 2 que el usuario probó. Es obligatorio probar el IPA reconstruido en el iPhone antes de distribuirlo.

## Atribución y licencia

S4NTOS INJECTOR es una variante con personalización visual y contactos del cliente; **no es una aplicación creada desde cero por S4NTOS**. El programa subyacente deriva de 3105 y de otras contribuciones. Se conservan el archivo GPL-3.0 `LICENSE` y `THIRD_PARTY_NOTICES.md` originales tanto en el checkout como dentro del paquete IPA reconstruido. No alteres ni elimines esos avisos al distribuirlo.

## Estados

1. Parche de código fuente: creado.
2. Workflow experimental: configurado.
3. Compilación macOS: pendiente de comprobar en GitHub Actions.
4. Instalación y funcionamiento GBox/ESign: pendiente de prueba manual.
5. Fusión a `main`: solo después de confirmar funcionamiento.

## Diferencia frente al método anterior

Un `s.json` vacío solo impide agregar nuevas fuentes predeterminadas; **no borra las fuentes ya guardadas**. La nueva implementación vacía deliberadamente el cuerpo de las vistas Home y New. Las secciones Sources e Installed permanecen independientes.
