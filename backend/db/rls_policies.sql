-- Enable Row Level Security
ALTER TABLE public.generation_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only select their own data
CREATE POLICY "Users can view own history" 
ON public.generation_history 
FOR SELECT 
USING (auth.uid() = user_id);

-- Policy: Users can insert their own data
CREATE POLICY "Users can insert own history" 
ON public.generation_history 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own data (optional, if needed)
CREATE POLICY "Users can update own history" 
ON public.generation_history 
FOR UPDATE 
USING (auth.uid() = user_id);

-- Policy: Users can delete their own data (optional, if needed)
CREATE POLICY "Users can delete own history" 
ON public.generation_history 
FOR DELETE 
USING (auth.uid() = user_id);
