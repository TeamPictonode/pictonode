// GNU AGPL v3 License
// Written by John Nunley

// Timeout for the given number of milliseconds.
export async function timeout(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
