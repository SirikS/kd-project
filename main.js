angular.module('KRRclass', [ 'chart.js']).controller('MainCtrl', ['$scope','$http', mainCtrl]);


function mainCtrl($scope, $http){


	$scope.launchMyGreatApp = function(){

		$scope.myDisplayMessage = "Welcome to my great Web Application called: " + $scope.myInputAppName ;
		$scope.mySparqlEndpoint = $scope.myInputEndPoint ;
    $scope.mySparqlQuery = encodeURI($scope.myInputQuery).replace(/#/, '%23');


    $http( {
     	method: "GET",
      url : $scope.mySparqlEndpoint + "?query=" + $scope.mySparqlQuery,
			headers : {'Accept':'application/sparql-results+json', 'Content-Type':'application/sparql-results+json'}
    	} )
    	.success(function(data, status ) {
			$scope.myDynamicLabels = [];
			$scope.myDynamicData = [];

			// now iterate on the results
			angular.forEach(data.results.bindings, function(val) {
    		$scope.myDynamicLabels.push(val.teacher.value);
    		$scope.myDynamicData.push(val.nbr_courses.value);
			});
      })
    	.error(function(error ){
    	    console.log('Error '+error);
    	});

	};

}
