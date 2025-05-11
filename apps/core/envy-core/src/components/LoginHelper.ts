import jwt, { SignOptions, JwtPayload } from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'AUTH_KEY'; // Secure via .env

export interface TokenPayload extends JwtPayload {
    uid: string;
    role?: string;
}

const signToken = (payload: TokenPayload, options?: SignOptions): string => {
    return jwt.sign(payload, JWT_SECRET, {
        algorithm: 'HS256',
        expiresIn: '1h',
        issuer: 'envybase',
        ...options,
    });
};

const verifyToken = (token: string): TokenPayload => {
    return jwt.verify(token, JWT_SECRET) as TokenPayload;
};

const decodeToken = (token: string): null | TokenPayload => {
    return jwt.decode(token) as TokenPayload | null;
};

export { signToken, verifyToken, decodeToken };
