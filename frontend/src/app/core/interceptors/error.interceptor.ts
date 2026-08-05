import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

/**
 * Traduce errores HTTP crudos a un mensaje legible en espanol, consistente
 * con el formato de error que devuelve el backend (ver core/error_handlers.py).
 * No oculta el error: lo deja pasar (rethrow) para que cada componente
 * decida como mostrarlo, pero ya normalizado.
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let mensaje = 'Ocurrio un error inesperado. Intenta de nuevo.';

      if (error.status === 0) {
        mensaje = 'No se pudo contactar al servidor. Verifica que el backend este corriendo.';
      } else if (error.error?.detail) {
        mensaje =
          typeof error.error.detail === 'string'
            ? error.error.detail
            : JSON.stringify(error.error.detail);
      } else if (error.error?.mensaje) {
        mensaje = error.error.mensaje;
      } else if (error.status === 404) {
        mensaje = 'El recurso solicitado no existe.';
      } else if (error.status >= 500) {
        mensaje = 'Error interno del servidor. Revisa los logs del backend.';
      }

      return throwError(() => ({ ...error, mensajeAmigable: mensaje }));
    }),
  );
};
