import { createContext } from 'react';
import { brand } from '../branding/brand';

export const AuthContext = createContext({ user: brand.operatorName, mode: 'development' });
