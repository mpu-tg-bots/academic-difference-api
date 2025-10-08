import baseConfig from '@gravity-ui/eslint-config';
import importOrderConfig from '@gravity-ui/eslint-config/import-order';
import prettierConfig from '@gravity-ui/eslint-config/prettier';
import serverConfig from '@gravity-ui/eslint-config/server';
import typescriptConfig from '@gravity-ui/eslint-config/typescript';

/**
 * @type {import('eslint').ESLint.ConfigData[]}
 */
export default [
    ...baseConfig,
    ...serverConfig,
    ...importOrderConfig,
    ...prettierConfig,
    ...typescriptConfig,
    {
        ignores: ['npm-debug.log', 'node_modules', 'build', 'dist', '*.json'],
        rules: {
            'import/no-extraneous-dependencies': [
                'error',
                {
                    devDependencies: false,
                    optionalDependencies: false,
                    peerDependencies: false,
                },
            ],
        },
    },
    {
        ...typescriptConfig[0],
        rules: {
            ...typescriptConfig[0].rules,
            '@typescript-eslint/consistent-type-imports': [
                'error',
                {fixStyle: 'inline-type-imports'},
            ],
        },
    },
];
