#define MIN(a, b)  (((a) < (b)) ? (a) : (b))
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))

#include <stdio.h>
#include <math.h>

int compute_g(unsigned char * pdata,int sizeX,int sizeY,double off_x,double off_y,double *TRIANGLE,double *DATA,double *LUT) {
	int bbx0,bby0,bbx1,bby1;
	int xint,yint;
	long int pos;
	unsigned char *pimage;

	double a0,b0,c0,a1,b1,c1,a2,b2,c2;
	double s0,s1,s2;
	double x0,y0,x1,y1,x2,y2,x,y;

	double mx0,my0,mx1,my1,mx2,my2;

	double xcentre,ycentre,xr,yr;
	double alpha,surf,surfalpha,value,totalvalue,gmin,gmax;
	double n;

	double sumX,sumY,sumXw,sumYw;

	pimage = (unsigned char*)pdata;

	mx0 = TRIANGLE[0]+off_x;
	my0 = TRIANGLE[1]+off_y;
	mx1 = TRIANGLE[2]+off_x;
	my1 = TRIANGLE[3]+off_y;
	mx2 = TRIANGLE[4]+off_x;
	my2 = TRIANGLE[5]+off_y;

	x0 = mx1;
	y0 = my1;
	x1 = mx0;
	y1 = my0;
	x2 = mx2;
	y2 = my2;

	//bounding box du triangle
	bbx0 = (int)(MIN(MIN(x0,x1),x2))-1;
	bbx1 = (int)(MAX(MAX(x0,x1),x2))+1;
	bby0 = (int)(MIN(MIN(y0,y1),y2))-1;
	bby1 = (int)(MAX(MAX(y0,y1),y2))+1;

	//centre du triangle
	xcentre = (x0+x1+x2)/3.0;
	ycentre = (y0+y1+y2)/3.0;

	//calcul des droites
	if(x0==x1){
		a0 = 1.0;
		b0 = 0.0;
		c0 = -x0;
	}
	else{
		if(y0==y1){
			a0 = 0.0;
			b0 = 1.0;
			c0 = -y0;
		}
		else{
			a0 = 1.0/(x1-x0);
			b0 = -1.0/(y1-y0);
			c0 = y0/(y1-y0) - x0/(x1-x0);
		}
	}
	//normalisation des a,b,c
	n = sqrt(a0*a0+b0*b0);	a0 /= n; b0/= n; c0 /= n;
	if ((a0*x2+b0*y2+c0) > 0) s0 = 1.0; else s0 = -1.0;
	x0 = mx1;
	y0 = my1;
	x1 = mx2;
	y1 = my2;
	x2 = mx0;
	y2 = my0;

	if(x0==x1){
		a1 = 1.0;
		b1 = 0.0;
		c1 = -x0;
	}
	else{
		if(y0==y1){
			a1 = 0.0;
			b1 = 1.0;
			c1 = -y0;
		}
		else{
			a1 = 1.0/(x1-x0);
			b1 = -1.0/(y1-y0);
			c1 = y0/(y1-y0) - x0/(x1-x0);
		}
	}
	//normalisation des a,b,c
	n = sqrt(a1*a1+b1*b1);	a1 /= n; b1/= n; c1 /= n;
	if ((a1*x2+b1*y2+c1) > 0.0) s1 = 1.0; else s1 = -1.0;

	x0 = mx0;
	y0 = my0;
	x1 = mx2;
	y1 = my2;
	x2 = mx1;
	y2 = my1;

	if(x0==x1){
		a2 = 1.0;
		b2 = 0.0;
		c2 = -x0;
	}
	else{
		if(y0==y1){
			a2 = 0.0;
			b2 = 1.0;
			c2 = -y0;
		}
		else{
			a2 = 1.0/(x1-x0);
			b2 = -1.0/(y1-y0);
			c2 = y0/(y1-y0) - x0/(x1-x0);
		}
	}
	//normalisation des a,b,c
	n = sqrt(a2*a2+b2*b2);	a2 /= n; b2/= n; c2 /= n;
	if ((a2*x2+b2*y2+c2) > 0.0) s2 = 1.0; else s2 = -1.0;

	//Remplissage du tableau
	surf = 0.0f;
	surfalpha = 0.0f;
	totalvalue =  0.0f;
	gmax = 0.0f;
	gmin = 1e31;
	sumX=sumY=sumXw=sumYw = 0.0;
	for(xint=bbx0;xint<=bbx1;xint++)
	{
		for(yint=bby0;yint<=bby1;yint++){
			pos = xint +yint * sizeX; //weave + linux ok ?
			//pos = xint + (sizeY-yint) * sizeX; //ligne par ligne ! librairie utilisée sous linux...
			//pos = yint + xint * sizeY;
			x = (double)xint;
			y = (double)yint;
			xr = x - xcentre;
			yr = y - ycentre;
			if((((a0*x+b0*y+c0)*s0)>=0.0)&&
				(((a1*x+b1*y+c1)*s1)>=0.0)&& //alpha du flou
				(((a2*x+b2*y+c2)*s2)>=0.0))
			{
				alpha = MIN(fabs(a0*x+b0*y+c0),1.0) * MIN(fabs(a1*x+b1*y+c1),1.0) * MIN(fabs(a2*x+b2*y+c2),1.0); //1 � l'int�rieur du triangle et sur les bords <1 droite normalis� donne la distance
				value = (double)(LUT[*(pimage+pos)]);//LUT[*(pimage+pos)];//lut[*(pimage+pos)];
				sumX += xr*alpha;
				sumY += yr*alpha;
				sumXw += xr*alpha*value;
				sumYw += yr*alpha*value;
				surfalpha += alpha;//
				surf += 1;//crisp
				totalvalue += (value*alpha);
				gmin = MIN(gmin,value);
				gmax = MAX(gmax,value);

			}
		}
	}
	if(surfalpha>0.0){
		sumX /= surfalpha;
		sumY /= surfalpha;

		sumX += xcentre;
		sumY += ycentre;
	}

	if(totalvalue>0.0){
		sumXw /= totalvalue;
		sumYw /= totalvalue;

		sumXw += xcentre;
		sumYw += ycentre;
	}else
	{
		sumXw = xcentre;//m_p0.mX;
		sumYw = ycentre;//m_p0.mY;
	}


	DATA[0] = (double)sumXw;//centroid
	DATA[1] = (double)sumYw;//centroid
	DATA[2] = (double)surf;//surfCrisp
	DATA[3] = (double)surfalpha;//surfAlpha
	DATA[4] = (double)totalvalue;//sum
	DATA[5] = (double)gmax; //max
	DATA[6] = (double)gmin; //min
	if(surfalpha>0.0)
		DATA[7] = (double)(totalvalue/surfalpha);//mean
	else
		DATA[7] = (double)0.0;


	return 0;
}



