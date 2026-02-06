import { Head, Html, Main, NextScript } from "next/document"

export default function Document() {
  return (
    <Html lang="en" className="dark">
      <Head>
        <meta name="theme-color" content="#061017" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="color-scheme" content="dark" />
        <meta
          name="description"
          content="Telemetry interpretation console for predictive fleet maintenance."
        />
        <link rel="icon" href="/logo.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Manrope:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <body className="aurora-bg text-text-primary antialiased overflow-x-hidden">
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
