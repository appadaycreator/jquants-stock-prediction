import "@testing-library/jest-dom";
// Web API ポリフィル（NextRequestで必要）
// Node18 では存在するが、Jest環境で未定義の場合があるため最小実装を用意
// NextRequestがURL getterのみを持つため、jest環境ではset不可エラーにならないような簡易Request実装
// 直接this.urlへ代入せず、コンストラクタ引数を保持してgetterで返す
if (typeof global.Request === "undefined") {
  // @ts-ignore
  global.Request = class {
    constructor(input, _init) {
      this._url = typeof input === "string" ? input : input?.url ?? "";
    }
    get url() {
      return this._url;
    }
  };
}
if (typeof global.Headers === "undefined") {
  // @ts-ignore
  global.Headers = class {};
}
if (typeof global.Response === "undefined") {
  // @ts-ignore
  global.Response = class {};
}

// Mock Next.js router
jest.mock("next/router", () => ({
  useRouter() {
    return {
      route: "/",
      pathname: "/",
      query: {},
      asPath: "/",
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn().mockResolvedValue(undefined),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    };
  },
}));

// Mock Next.js navigation
jest.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    };
  },
  useParams() {
    return {};
  },
  usePathname() {
    return "/";
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock fetch
global.fetch = jest
  .fn()
  .mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock scrollIntoView
if (typeof HTMLElement !== "undefined") {
  // @ts-ignore
  HTMLElement.prototype.scrollIntoView = jest.fn();
}

// Spy console methods to avoid noisy output and allow expectations
if (typeof console !== "undefined") {
  // eslint-disable-next-line no-console
  jest.spyOn(console, "debug").mockImplementation(() => {});
  // eslint-disable-next-line no-console
  jest.spyOn(console, "info").mockImplementation(() => {});
  // eslint-disable-next-line no-console
  jest.spyOn(console, "warn").mockImplementation(() => {});
  // eslint-disable-next-line no-console
  jest.spyOn(console, "error").mockImplementation(() => {});
}

// Mock next/server for NextRequest minimal behavior in Jest
jest.mock("next/server", () => {
  try {
    // Prefer real NextResponse if available to preserve behavior
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const actual = require("next/server");
    class MockNextRequest {
      constructor(input) {
        this.url = typeof input === "string" ? input : input?.url ?? "";
        this.nextUrl = new URL(this.url || "http://localhost/");
        this.headers = new Map();
        this.cookies = { get: jest.fn().mockReturnValue(undefined) };
      }
    }
    return { ...actual, NextRequest: MockNextRequest };
  } catch (_e) {
    class MockNextRequest {
      constructor(input) {
        this.url = typeof input === "string" ? input : input?.url ?? "";
        this.nextUrl = new URL(this.url || "http://localhost/");
        this.headers = new Map();
        this.cookies = { get: jest.fn().mockReturnValue(undefined) };
      }
    }
    const NextResponse = {
      json: (data, init = {}) => ({
        ok: true,
        status: init.status ?? 200,
        headers: init.headers ?? {},
        async json() {
          return data;
        },
      }),
    };
    return { NextRequest: MockNextRequest, NextResponse };
  }
});