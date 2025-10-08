import type {Config} from '@jest/types';

const nodeConfig: Config.InitialOptions = {
    displayName: 'Server',
    preset: 'ts-jest',
    modulePathIgnorePatterns: ['__mocks__'],
    rootDir: '.',
    roots: ['<rootDir>/src'],
    testEnvironment: 'node',
    testMatch: ['**/*.test.(ts|js)'],
    transform: {
        '\\.[tj]sj?$': ['ts-jest', {tsconfig: '<rootDir>/tsconfig.json'}],
    },
    transformIgnorePatterns: [],
};

const config: Config.InitialOptions = {
    projects: [{...nodeConfig}],
    passWithNoTests: true,
};

export default config;
