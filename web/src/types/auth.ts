export type UserType = 'property_manager' | 'contractor' | 'tenant' | 'admin'

export interface User {
  id: string
  email: string
  full_name: string
  user_type: UserType
  organization_id?: string
  email_verified: boolean
  phone_verified: boolean
  created_at: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface RegisterData {
  email: string
  password: string
  user_type: UserType
  full_name: string
  phone?: string
  organization_name?: string
}

export interface LoginData {
  email: string
  password: string
}