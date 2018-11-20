<template>
  <v-container fluid grid-list-md>
    <v-slide-y-transition mode="out-in">
      <v-layout row wrap align-center>
        <v-flex v-for="article in articles">
          <v-card>
            <v-card-title>
              <span class="headline"><a v-bind:href="article.url" target="_blank">{{ article.h1 }}</a></span>
            </v-card-title>
            <v-card-text>
              <blockquote>
                FacebookScore: {{ article.score }}
                <footer>
                  <small>
                    <em>&mdash;{{ article.paragraph }}</em>
                  </small>
                </footer>
              </blockquote>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-slide-y-transition>
  </v-container>
</template>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<script>
import axios from 'axios'

export default {
  data () {
    return {
      articles: []
    }
  },
  mounted: function () {
    console.log('mounted')
    // APIを叩く。
    // 開発サーバで動作中はちゃんとDjangoの8000番ポートを叩いてくれます。
    axios.get('/api/articles/')
      .then((response) => {
        this.articles = response.data
      })
      .catch((error) => {
        console.log(error)
      })
  }
}
</script>
