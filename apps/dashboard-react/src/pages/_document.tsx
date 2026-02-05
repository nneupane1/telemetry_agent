
import { Html, Head, Main, NextScript } from "next/document"

export default function Document() {
  return (
    <Html lang="en" className="dark">
      <Head>
        {/* Primary theme color for browser UI */}
        <meta name="theme-color" content="#05070D" />

        {/* Performance & rendering hints */}
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="color-scheme" content="dark" />

        {/* Favicon (placeholder, replace later) */}
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <body
        className="
          bg-bg-primary
          text-text-primary
          antialiased
          overflow-x-hidden
        "
      >
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
