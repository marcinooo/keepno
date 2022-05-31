const path = require('path');

module.exports = {
  mode: 'production',
  entry: {
    header: {
      import: './src/header.js',
      dependOn: ['utils', 'alerts'],
    },
    note: {
      import: './src/note.js',
      dependOn: ['utils', 'alerts'],
    },
    export_note: {
      import: './src/export_note.js',
      dependOn: 'alerts',
    },
    alerts: {
      import: './src/alerts.js',
    },
    utils: {
      import: './src/utils.js',
    }
  },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, '..', 'app', 'static', 'js'),
  },
  module: {
    rules: [
      {
        test: /\.m?js$/,
        exclude: /(node_modules|bower_components)/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: ['@babel/plugin-proposal-class-properties'],
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ],
  },
  externals: {
    jquery: 'bootstrap',
  },
  optimization: {
    runtimeChunk: 'single',
  },
};
