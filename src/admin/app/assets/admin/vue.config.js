module.exports = {
    outputDir: '../../public/build',
//    publicPath: 'http://192.168.1.49:8080/build',
    publicPath: '/build',
    css: {
        sourceMap: true,
        extract: true
    },
    filenameHashing: true,
    // devServer: {
    //     headers: { "Access-Control-Allow-Origin":"\*" },
    //     disableHostCheck: true,
    //     public: '192.168.1.49:8080',
    // },
    configureWebpack: {
        //module: {

            // rules: [
            //     {

            //     {
            //         test: /\.(woff|woff2|eot|ttf|svg)$/,
            //         exclude: /node_modules/,
            //         use: [
            //             {
            //                 loader: 'file-loader',
            //                 options: {
            //                     name: '[path][name].[ext]',
            //                     publicPath: '../',
            //                     emitFile: false,
            //                     sourceMap: false
            //                 }
            //             }
            //         ]
            //     }

            // ]

    },
    chainWebpack: config => {
        config.devtool('source-map')

        // disable chunks
        //config.optimization.delete('splitChunks')

        // disable js minify
        config.optimization.minimize(false)

        // disable css minify
        config.plugins.delete('optimize-css')

        // disable html generation
        config.plugins.delete('html')
        config.plugins.delete('preload')
        config.plugins.delete('prefetch')

        //generate manifest json
        config.plugin('webpack-assets-manifest')
        .use(require('webpack-assets-manifest'))
        .tap(args => {
            return [ {output: 'manifest.json', publicPath: true} ]
        })

        //remove mains.js entry point
        config.entryPoints.delete('app')

        config.entry('login').add('./src/login.js').end()
            .entry('admin').add('./src/admin.js').end()
            .entry('admin-projects').add('./src/admin-projects.js').end()
            .entry('admin-project').add('./src/admin-project.js').end()
            .entry('icons').add('./src/icons/icons.js').end()

        //icon font generation
        config.module.rule('icons').test(/\.icons$/)
            .use('icons-css').loader(
              process.env.NODE_ENV === 'development'
                ? 'vue-style-loader'
                : require('mini-css-extract-plugin').loader
            ).end()
            .use('icons-css').loader(require('mini-css-extract-plugin').loader).end()
            .use('css-loader').loader('css-loader').end()
            .use('webfonts-loader').loader('webfonts-loader').end()
    }

}
