//-----------------------------------------------------------------------
// <copyright company="Microsoft Corporation">
//        Copyright (c) Microsoft Corporation.  All rights reserved.
//        Licensed under the MIT license. See LICENSE file in the project root for full license information.
// </copyright>
//-----------------------------------------------------------------------

import { type ReactNode } from 'react';

import { useAuth } from '@/hooks/auth.context';

interface AuthGateProps {
  children: ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const {
    isLoading,
    isAuthenticated,
    canSignIn,
    signIn,
    isSigningIn,
    signInError,
    config,
    error,
  } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-sm text-muted-foreground">
          Conectando con Fabric…
        </div>
      </div>
    );
  }

  if (config.kind === 'not-deployed') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md text-center">
          <h2 className="mb-2 text-lg font-semibold text-foreground">
            Configura la app para iniciar sesión
          </h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Para iniciar sesión hace falta el backend de Fabric. Arranca{' '}
            <code className="rounded bg-muted px-1 py-0.5">npm run dev</code>{' '}
            con un área de trabajo aprobada o despliega la app, y recarga la página.
          </p>
        </div>
      </div>
    );
  }

  if (config.kind === 'incomplete') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md text-center">
          <h2 className="mb-2 text-lg font-semibold text-foreground">
            Falta la configuración de Rayfin
          </h2>
          <p className="mb-4 text-sm text-muted-foreground">
            El servidor de desarrollo arrancó sin {config.missing.join(', ')}.
            Revisa los avisos que mostró y vuelve a arrancarlo.
          </p>
        </div>
      </div>
    );
  }

  if (config.kind === 'config-error') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md text-center">
          <h2 className="mb-2 text-lg font-semibold text-foreground">
            No se ha podido cargar la configuración de la app
          </h2>
          <p className="mb-4 text-sm text-muted-foreground">
            La app se ha detenido para no usar los valores con los que se
            compiló, que en otro entorno apuntarían al backend equivocado.
            Vuelve a desplegarla y recarga la página.
          </p>
          <p className="text-xs text-muted-foreground">{config.message}</p>
        </div>
      </div>
    );
  }

  if (error && !canSignIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 text-center shadow-lg">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-primary">
            Banco Brétema
          </p>
          <h2 className="mb-2 text-lg font-semibold text-card-foreground">
            No se ha podido iniciar sesión
          </h2>
          <p className="text-sm text-muted-foreground">{error.message}</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated && canSignIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md rounded-xl border border-border bg-card p-6 text-center shadow-lg">
          <img
            src="/emblema-bretema.png"
            alt=""
            width={64}
            height={64}
            className="mx-auto mb-4 size-16 rounded-xl"
          />
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-primary">
            Banco Brétema · Consola de alertas
          </p>
          <h2 className="mb-2 text-xl font-semibold text-card-foreground">
            {error ? 'No se ha podido iniciar sesión automáticamente' : 'Hola de nuevo'}
          </h2>
          {error ? (
            <p role="alert" className="mb-4 text-sm text-destructive">
              {error.message}
            </p>
          ) : (
            <p className="mb-6 text-sm text-muted-foreground">
              Inicia sesión con tu cuenta de Microsoft para abrir la consola.
            </p>
          )}
          <button
            type="button"
            className="w-full rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground shadow-sm transition hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isSigningIn}
            onClick={() => void signIn()}
          >
            {isSigningIn
              ? 'Iniciando sesión…'
              : error
                ? 'Reintentar el inicio de sesión'
                : 'Iniciar sesión con Microsoft'}
          </button>
          {signInError ? (
            <p role="alert" className="mt-4 text-sm text-destructive">
              {signInError.message}
            </p>
          ) : null}
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background p-4">
        <div className="w-full max-w-md text-center">
          <h2 className="mb-2 text-lg font-semibold text-foreground">
            El inicio de sesión no está disponible
          </h2>
          <p className="mb-4 text-sm text-muted-foreground">
            La app necesita una sesión autenticada. Revisa la configuración de
            autenticación y recarga la página.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
