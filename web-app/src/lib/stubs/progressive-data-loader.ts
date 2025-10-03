export const progressiveDataLoader = {
  async loadDataProgressively<T>(loader: (offset: number, limit: number) => Promise<T>, limit: number = 1000) {
    const data: any = await loader(0, limit);
    return { data } as { data: any };
  },
  cleanup() {},
};

export default progressiveDataLoader;

