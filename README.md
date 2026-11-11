# Iconos

Conversor de imágenes PNG, JPG y WebP a iconos multirresolución `.ico` para Windows.

**Versión oficial:** V0.1.5. Programa independiente, compatible con su futura integración en Suite de Programas B V0.3.3. La Suite no ha sido modificada.

## Funciones

- Selección y vista previa de imágenes.
- Conversión individual y por lotes.
- Siete tamaños: 16, 24, 32, 48, 64, 128 y 256 píxeles.
- Ajustes Centrar, Recortar y Estirar.
- Filtros Lanczos, Bicubic y selección automática experimental.
- Canal alfa y compresión PNG para la resolución mayor.
- Nombre y destino configurables para un archivo individual.
- Interfaz Windows con inicio maximizado y botón Salir.

## Instalación y actualizaciones

La distribución para Windows se genera con PyInstaller (`onedir`) e Inno Setup 6, que utiliza un `AppId` fijo y permite actualizar sobre la misma instalación. Los instaladores de nuevas versiones no deben eliminar archivos `.ico` personales. El programa no incluye imágenes ni iconos de demostración: solo su icono identificativo.

**Estado de publicación:** la publicación del instalador `Iconos_Setup_V0.1.5.exe` como archivo adjunto de una GitHub Release está pendiente hasta verificar la subida del binario. No sustituir el instalador oficial probado por una compilación distinta.

## Licencia y terceros

La implementación es independiente de Quick Any2Ico y de ImageToIcon; no contiene código extraído de esos programas. No se concede una licencia de redistribución de código fuente adicional mediante este README. Las dependencias conservan sus respectivas licencias.
