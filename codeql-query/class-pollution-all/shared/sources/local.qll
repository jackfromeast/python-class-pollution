// import python
// import semmle.python.ApiGraphs
// import semmle.python.dataflow.new.DataFlow

// module ClassPollutionRemoteSource {
//   /**
//    * Holds all the remote sources from python and popular libraries.
//    * 
//    * CodeQL models a very good amout of python frameworks, available at https://github.com/github/codeql/tree/987af4ce1df3d3225e5af63b1b3b1606644c3e61/python/ql/lib/semmle/python/frameworks
//    * We are extending this model to include more remote sources.
//    * 
//    * @param source
//    * @return true if the source is a remote source
//    */
//   predicate isLocalSource(DataFlow::Node source) {
//     source instanceof LocalSources
//   }
// }