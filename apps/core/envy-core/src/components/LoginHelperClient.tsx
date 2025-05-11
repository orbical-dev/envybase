export default async function CookieChecker() {
    return new Promise((resolve) => {
        const cookies = document.cookie;
        const accessTokenCookie = cookies.split('; ').find(row => row.startsWith('access_token='));
        
        if (accessTokenCookie) {
            const accessToken = accessTokenCookie.split('=')[1];

            resolve(accessToken.trim() !== "");
        } else {
            resolve(false);
        }
    });
}
