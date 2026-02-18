/// <reference types="vite/client" />

declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}

declare module '*?raw' {
    const content: string
    export default content
}

interface ImportMetaEnv {
    readonly VITE_TESTER_INTERNAL_SECRET: string
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
