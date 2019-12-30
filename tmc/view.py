from rest_framework import views
from rest_framework.response import Response

from .serializers import TMCSerializer
from .service import TMC
from .exceptions import TMCError, TMCWarning


class TMCView(views.APIView):
    def get(self, request):
        try:
            amount = request.query_params.get('amount', None)
            days = request.query_params.get('days', None)
            query_date = request.query_params.get('date', None)

            tmc_object = TMC.get_tmc_from_api(
                amount=amount,
                days=days,
                query_date=query_date
            )
        except TMCError as error:
            return Response({'error': str(error)}, status=400)
        except TMCWarning as warn:
            serializer = TMCSerializer(instance=warn.data)
            return Response({
                'warn': str(warn),
                'tmc': serializer.data['tmc']
            }, status=400)

        serializer = TMCSerializer(instance=tmc_object)
        return Response(serializer.data)
