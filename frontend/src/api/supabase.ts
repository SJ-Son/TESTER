
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
    console.warn('Supabase URL 또는 Key가 누락되었습니다. .env 설정을 확인해주세요.')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
