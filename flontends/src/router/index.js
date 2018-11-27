import Vue from 'vue'
import Router from 'vue-router'
import TopArticleList from '@/components/TopArticleList'
import Hoge from '@/components/Hoge'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'TopArticleList',
      component: TopArticleList
    },
    {
      path: '/hoge',
      name: 'Hoge',
      component: Hoge
    }
  ]
})
