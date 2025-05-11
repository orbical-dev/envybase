import "./globals.css";

export const metadata = {
    title: '404 | Envybase Frontend',
};


const NotFound = () => {
    return (
        <div className="flex flex-col items-center justify-center h-screen">
        <h1 className="text-4xl font-bold">404 - Not Found</h1>
        <p className="mt-4 text-lg">The page you are looking for does not exist.</p>
            <a className="rounded-full button border border-solid border-transparent transition-colors flex items-center justify-center bg-foreground text-background gap-2 hover:bg-[#383838] dark:hover:bg-[#ccc] font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto" href="/">Home</a>
        </div>
    );
}

export default NotFound;