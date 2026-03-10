export interface UserCredentials {
  username: string;
  password: string;
}

export interface RegisterData extends UserCredentials {
  email?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Parameter {
  name: string;
  app: string;
}

export interface ParameterRequest {
  app: string;
  name: string;
  value: string;
}

export interface ParameterResponse {
  name: string;
  message: string;
}
