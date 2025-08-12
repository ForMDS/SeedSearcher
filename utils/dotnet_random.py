# utils/dotnet_random.py
# 精确还原 C# System.Random（legacy RNG）

class DotNetRandom:
    MBIG = 2147483647
    MSEED = 161803398
    MZ = 0

    def __init__(self, Seed):
        self.SeedArray = [0] * 56
        self.inext = 0
        self.inextp = 21

        subtraction = Seed
        if subtraction == -2147483648:
            subtraction = 2147483647
        subtraction = abs(subtraction)

        mj = self.MSEED - subtraction
        if mj < 0:
            mj += self.MBIG
        self.SeedArray[55] = mj

        mk = 1
        for i in range(1, 55):
            ii = (21 * i) % 55
            self.SeedArray[ii] = mk
            mk = mj - mk
            if mk < 0:
                mk += self.MBIG
            mj = self.SeedArray[ii]

        for k in range(1, 5):
            for i in range(1, 56):
                self.SeedArray[i] -= self.SeedArray[1 + (i + 30) % 55]
                if self.SeedArray[i] < 0:
                    self.SeedArray[i] += self.MBIG

    def InternalSample(self):
        self.inext += 1
        if self.inext >= 56:
            self.inext = 1
        self.inextp += 1
        if self.inextp >= 56:
            self.inextp = 1

        retVal = self.SeedArray[self.inext] - self.SeedArray[self.inextp]
        if retVal == self.MBIG:
            retVal -= 1
        if retVal < 0:
            retVal += self.MBIG

        self.SeedArray[self.inext] = retVal
        return retVal

    def Sample(self):
        return self.InternalSample() * (1.0 / self.MBIG)

    def GetSampleForLargeRange(self):
        result = self.InternalSample()
        if self.InternalSample() % 2 == 0:
            result = -result
        d = result
        d += self.MBIG - 1
        return d / (2.0 * self.MBIG - 1)

    def Next(self, minValue=None, maxValue=None):
        if minValue is None:
            return self.InternalSample()
        if maxValue is None:
            if minValue < 0:
                raise ValueError("minValue must be non-negative.")
            return int(self.Sample() * minValue)
        if minValue > maxValue:
            raise ValueError("minValue must be less than maxValue.")
        range_ = maxValue - minValue
        if range_ <= self.MBIG:
            return int(self.Sample() * range_) + minValue
        return int(self.GetSampleForLargeRange() * range_) + minValue

    def NextDouble(self):
        return self.Sample()

    def NextBytes(self, buffer):
        for i in range(len(buffer)):
            buffer[i] = int(self.InternalSample() % 256)
